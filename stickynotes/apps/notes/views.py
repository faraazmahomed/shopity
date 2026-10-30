from django.shortcuts import get_object_or_404, redirect, render
from .forms import NoteForm
from .models import Note


def note_list(request):
    if request.method == "POST":
        form = NoteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("notes:note_list")
    else:
        form = NoteForm()

    notes = Note.objects.all()
    context = {
        "notes": notes,
        "form": form,
    }
    return render(request, "notes/note_list.html", context)


def note_delete(request, pk):
    note = get_object_or_404(Note, pk=pk)
    if request.method == "POST":
        note.delete()
        return redirect("notes:note_list")
    return redirect("notes:note_list")
