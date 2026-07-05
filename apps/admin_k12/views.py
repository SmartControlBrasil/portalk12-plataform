from pathlib import Path

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import redirect, render


AKADEMI_TEMPLATE_ROOT = (
    Path(settings.BASE_DIR)
    / "templates"
    / "admin-k12"
    / "akademi"
    / "pages"
)


@login_required
def dashboard(request):
    return redirect("admin_k12:akademi_page", page="index.html")


@login_required
def akademi_page(request, page):
    safe_page = page.strip("/")

    if not safe_page:
        safe_page = "index.html"

    if not safe_page.endswith(".html"):
        safe_page = f"{safe_page}.html"

    if ".." in safe_page:
        raise Http404("Página inválida.")

    template_path = AKADEMI_TEMPLATE_ROOT / safe_page

    if not template_path.exists():
        raise Http404(f"Página do Akademi não encontrada: {safe_page}")

    return render(request, f"admin-k12/akademi/pages/{safe_page}")
