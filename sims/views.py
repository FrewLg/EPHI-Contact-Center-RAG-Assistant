from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Plan
from .forms import PlanForm

import os, time, json, re

from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .forms import ChatForm 
# from .models import ChatSession, Message
# from .utils import generate_response

from django.conf import settings
from django.core.cache import cache  # simple rate-limiting with cache

 
# FHIR_API_URL = 'https://your-fhir-server.com/fhir/Patient'  # Replace with actual endpoint
# FHIR_API_TOKEN = 'your-auth-token'  # Optional if public or local
############


# def new_chat(request):
#     session = ChatSession.objects.create()
#     return redirect('healthchat:chat', id=str(session.id))


# def chat_view(request, id):
#     session = get_object_or_404(ChatSession, id=id)

#     if request.method == 'POST':
#         form = ChatForm(request.POST)
#         if form.is_valid():
#             user_input = form.cleaned_data['user_input']

#             recent_messages = session.messages.order_by('-created')[:3][::-1]
#             ai_response = generate_response(user_input, recent_messages)

#             Message.objects.create(session=session, sender='human', text=user_input)
#             Message.objects.create(session=session, sender='ai', text=ai_response)

#             return redirect('chats:chat', id=session.id)

#     else:
#         form = ChatForm()

#     chat_history = session.messages.order_by('created')

#     return render(request, 'healthchat/chat.html', {
#         'form': form,
#         'chat_history': chat_history,
#         'session': session,
#     })
# ?############
PHI_PATTERNS = [
    r"\b\d{3}-\d{2}-\d{4}\b",  # SSN pattern
    r"\b\d{3} \d{2} \d{4}\b",
    r"\b\d{10}\b",
    # add more heuristics
]

def contains_phi(text):
    for p in PHI_PATTERNS:
        if re.search(p, text):
            return True
    return False

def rate_limit(request, limit=20, period=60):
    ip = request.META.get("REMOTE_ADDR", "anonymous")
    key = f"rl:{ip}"
    data = cache.get(key) or {"count": 0, "ts": time.time()}
    if time.time() - data["ts"] > period:
        data = {"count": 0, "ts": time.time()}
    data["count"] += 1
    cache.set(key, data, timeout=period)
    return data["count"] <= limit

def chat_page(request):
    # Render chat UI with disclaimer
    return render(request, "chatbot/chat.html", {
        "disclaimer": (
            "This chatbot provides informational content only and is not a substitute "
            "for professional medical advice. If you are experiencing a medical emergency, call your local emergency number."
        )
    })

@require_POST
def message_proxy(request):
    # Rate limit
    if not rate_limit(request, limit=30, period=60):
        return JsonResponse({"error": "Too many requests. Try again later."}, status=429)

    form = ChatForm(request.POST)
    if not form.is_valid():
        return HttpResponseBadRequest("Invalid input")

    user_message = form.cleaned_data["message"].strip()
    if not user_message:
        return JsonResponse({"error": "Empty message"}, status=400)

    # Basic PHI check
    if contains_phi(user_message):
        return JsonResponse({
            "error": "Messages that appear to contain personally identifiable or sensitive information are blocked. Please remove identifiers and try again."
        }, status=400)

    # Guardrails for emergency/self-harm flags (simplified — use a proper classifier in prod)
    if re.search(r"\b(suicid|kill myself|harm myself|self harm)\b", user_message, re.I):
        return JsonResponse({
            "error": "This message appears to indicate self-harm or danger. Please contact local emergency services or a crisis hotline."
        }, status=400)

    # Call external inference API (server-side)
    api_key = os.environ.get("CHAT_API_KEY") or getattr(settings, "CHAT_API_KEY", None)
    api_endpoint = os.environ.get("CHAT_API_ENDPOINT") or getattr(settings, "CHAT_API_ENDPOINT", None)
    if not api_key or not api_endpoint:
        return JsonResponse({"error": "Server not configured with chat API key/endpoint"}, status=500)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Build payload for HF inference endpoint: adapt per provider
    payload = {
        "inputs": user_message,
        # for models that accept parameters in 'parameters' or 'options'
        "options": {"wait_for_model": True}
    }

    try:
        resp = requests.post(api_endpoint, headers=headers, json=payload, timeout=30)
    except requests.RequestException as e:
        return JsonResponse({"error": "Failed to reach inference API", "detail": str(e)}, status=502)

    if resp.status_code != 200:
        # pass error message from API but sanitize
        try:
            err = resp.json()
        except Exception:
            err = resp.text
        return JsonResponse({"error": "Model API error", "detail": err}, status=502)

    # Parse model response — HF typically returns {"generated_text": "..."} or text; adapt to model
    try:
        res_json = resp.json()
        # Many HF text-generation models return [{"generated_text": "..."}] or {"generated_text": "..."}. Detect common forms.
        if isinstance(res_json, list) and len(res_json) and "generated_text" in res_json[0]:
            model_text = res_json[0]["generated_text"]
        elif isinstance(res_json, dict) and "generated_text" in res_json:
            model_text = res_json["generated_text"]
        elif isinstance(res_json, dict) and "error" in res_json:
            return JsonResponse({"error": "Model error", "detail": res_json["error"]}, status=502)
        else:
            # fallback: if the API returns string
            model_text = str(res_json)
    except ValueError:
        model_text = resp.text

    # Post-process: strip dangerous instructions (simplified). For production use robust filters or a safety model.
    model_text = model_text.strip()

    # Return answer
    return JsonResponse({"reply": model_text})

# =======
@csrf_exempt
def send_patient(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        fhir_payload = {
            "resourceType": "Patient",
            "name": [{"given": [data['name']], "family": "Legese"}],
            "gender": data['gender'],
            "birthDate": data['birth_date']
        }
        headers = {
            'Authorization': f'Bearer {FHIR_API_TOKEN}',
            'Content-Type': 'application/fhir+json'
        }
        response = requests.post(FHIR_API_URL, json=fhir_payload, headers=headers)
        return JsonResponse({'status': response.status_code, 'response': response.json()})
     
def home(request):
    return render(request, 'home.html')
def plan_list(request):
    plans = Plan.objects.all()
    return render(request, 'plan/plan_list.html', {'plans': plans})


def plan_create(request):
    form = PlanForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        plan = form.save(commit=False)
        plan.submitted_by = request.user
        plan.save()
        return redirect('plan_list')
    return render(request, 'plan/plan_form.html', {'form': form})

def plan_update(request, pk):
    plan = get_object_or_404(Plan, pk=pk)
    form = PlanForm(request.POST or None, request.FILES or None, instance=plan)
    if form.is_valid():
        form.save()
        return redirect('plan_list')
    return render(request, 'plan/plan_form.html', {'form': form})

def plan_delete(request, pk):
    plan = get_object_or_404(Plan, pk=pk)
    if request.method == 'POST':
        plan.delete()
        return redirect('plan_list')
    return render(request, 'plan/plan_confirm_delete.html', {'plan': plan})
