"""
View controllers handling CRUD operations and list rendering for sticky notes.
"""

from django.shortcuts import render, get_object_or_404, redirect
from .models import Note
from .forms import NoteForm

def note_list(request):
    """
    Displays all notes ordered with pinned notes first, followed by creation date.
    """
    notes = Note.objects.order_by('-is_pinned', '-created_at')
    return render(request, 'notes/note_list.html', {'notes': notes})

def note_detail(request, pk):
    """
    Displays the detailed view for a specific note identified by primary key.
    """
    note = get_object_or_404(Note, pk=pk)
    return render(request, 'notes/note_detail.html', {'note': note})

def note_create(request):
    """
    Handles the creation of a new note via form submission.
    """
    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('notes:note_list')
    else:
        form = NoteForm()
    return render(request, 'notes/note_form.html', {'form': form})

def note_update(request, pk):
    """
    Handles updating an existing note identified by primary key.
    """
    note = get_object_or_404(Note, pk=pk)
    if request.method == 'POST':
        form = NoteForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            return redirect('notes:note_list')
    else:
        form = NoteForm(instance=note)
    return render(request, 'notes/note_form.html', {'form': form, 'note': note})

def note_delete(request, pk):
    """
    Handles the deletion confirmation and removal of an existing note.
    """
    note = get_object_or_404(Note, pk=pk)
    if request.method == 'POST':
        note.delete()
        return redirect('notes:note_list')
    return render(request, 'notes/note_confirm_delete.html', {'note': note})
