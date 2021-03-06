import os
import random
from datetime import datetime
from io import BytesIO

from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa


def photo_path(instance, filename):
    basefilename, file_extension = os.path.splitext(filename)
    chars = '1234567890'
    randomstr = ''.join((random.choice(chars)) for x in range(3))
    year = datetime.now().year
    month = datetime.now().month
    directory = instance.folder
    return '{path}/{year}/{month}/{basename}-{randomstring}{ext}'.format(year=year,
                                                                         month=month, basename=basefilename,
                                                                         randomstring=randomstr, ext=file_extension,
                                                                         path=directory)


def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()

    # PDF
    pdf = pisa.pisaDocument(BytesIO(html.encode("utf-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None
