#!/usr/bin/env python

import os
import urllib2
from reportlab.lib.pagesizes import A3
from reportlab.platypus import SimpleDocTemplate, Image

doc = SimpleDocTemplate("image.pdf", pagesize=A3)
parts = []
parts.append(Image(
    "C:/Users/yuanjiexiong/Desktop/4strip/1612-LK8H.02-CD3/_PIE_1612-LK8H.02-CD3.png"))
doc.build(parts)
