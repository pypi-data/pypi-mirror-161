#   Copyright 2020 Frances M. Skinner, Christian Hill
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from django.shortcuts import render, get_object_or_404
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.decorators import user_passes_test
from .models import Ref, get_ref_from_doi
from .utils import canonicalize_doi
from .forms import RefForm
from .filters import RefFilter


def user_can_edit(u):
    return u.groups.filter(name="can-edit-refs").exists() or u.is_superuser


# @user_passes_test(user_can_edit)
def edit(request, pk=None):
    c = {"pk": pk if pk else ""}
    if request.method == "POST":
        ref = None
        if pk:
            ref = Ref.objects.get(pk=pk)
        form = RefForm(request.POST, instance=ref)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/refs/")
    else:
        try:
            ref = Ref.objects.get(pk=pk)
        except Ref.DoesNotExist:
            ref = None
        form = RefForm(instance=ref)

    c["form"] = form
    return render(request, "refs/edit.html", c)


def resolve(request, pk=None):
    # Look up DOI and pre-populate form, render to refs/add.html
    if request.method == "GET":
        doi = request.GET.get("doi")
        doi = canonicalize_doi(doi)
        if not pk:
            try:
                # We're trying to add a reference but one with the same DOI
                # is in the database already.
                ref = Ref.objects.get(doi=doi)
                return HttpResponseRedirect(f"/refs/edit/{ref.pk}")
            except Ref.DoesNotExist:
                ref = None
        else:
            ref = get_object_or_404(Ref, pk=pk)
        ref = get_ref_from_doi(doi, ref)
        form = RefForm(instance=ref)
        c = {"form": form, "pk": pk if pk else ""}
        # return edit(request, pk=pk)
        # url = reverse('ref:edit', kwargs={'pk': pk})
        return render(request, "refs/edit.html", c)
    raise Http404


def ref_list(request):
    refs = Ref.objects.all()
    paginator = Paginator(refs, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    c = {"page_obj": page_obj, "paginator": paginator}
    return render(request, "refs/refs-list.html", c)


# @user_passes_test(user_can_edit)
def delete(request, pk):
    ref = get_object_or_404(Ref, pk=pk)
    ref.delete()
    return HttpResponseRedirect("/refs/")


def search(request):
    ref_list = Ref.objects.all()
    ref_filter = RefFilter(request.GET, queryset=ref_list)
    nresults = ref_filter.qs.count()
    filtered_qs = sorted(ref_filter.qs, key=lambda objects: objects.pk)

    paginator = Paginator(filtered_qs, 10)

    c = {}
    if request.GET:
        page = request.GET.get("page")
        try:
            response = paginator.page(page)
        except PageNotAnInteger:
            response = paginator.page(1)
        except EmptyPage:
            response = paginator.page(paginator.num_pages)

        querydict = request.GET.copy()
        try:
            del querydict["page"]
        except KeyError:
            pass
        c["querystring"] = "&" + querydict.urlencode()
    else:
        response = None

    c.update(
        {
            "filter": ref_filter,
            "filtered_refs": response,
            "nresults": nresults,
            "paginator": paginator,
        }
    )
    return render(request, "refs/search.html", c)
