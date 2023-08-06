## -*- coding: utf-8; -*-
<%inherit file="/form.mako" />

<%def name="title()">New ${model_title_plural if master.creates_multiple else model_title}</%def>

${parent.body()}
