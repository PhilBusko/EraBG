"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
COMMON/TEMPLATETAGS/UTILITY_TTAGS.py
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

import os
from random import randint

from django import template
from django.utils.html import format_html
from django.conf import settings

import common.utility as CU

# function decorator
register = template.Library()


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
HTML EDIT TEXT
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


@register.simple_tag
def ctrl_label(name, value="", cssClass=""):
    html = format_html("""
        <div class="inner_margin2 {}">
            <span id="{}_label" class=""> {} </span>
        </div>
        """,
        cssClass, name, value);
    return html


@register.simple_tag
def ctrl_status(name):
    html = format_html("""
        <div class="inner_margin2">
            <span id="{}_status" class="font_small"
                style="white-space: normal; word-wrap: normal; text-align: right;"> </span>
        </div>
        """,
        name);
    return html


@register.simple_tag
def ctrl_link(name, label):
    html = format_html("""
        <div class="inner_margin2">
            <span id="{}_link" class="font_link">{}</span>
        </div>""",
        name, label);
    return html


@register.simple_tag
def ctrl_linkA(name, url, label, othertab=False):
    html = format_html("""
        <div class="inner_margin2">
            <a id="{}_link" class="font_link font_strong" {} href="{}">{}</a>
        </div>""",
        name, ('target="blank"' if othertab else ""), url, label);
    return html


@register.simple_tag
def ctrl_listing(name, label, value=""):   
    html = format_html("""
        <div class="display_cellM">
            <span class="inner_margin2" style=""><b>{}:</b></span>
        </div>
        <div class="display_cellM">
            <span class="inner_margin2" id="{}_listing"> {} </span>
        </div>
        """,
        label, name, value);
    return html


@register.simple_tag
def ctrl_entry(name):
    html = format_html("""
        <div class="inner_margin2" style="">
            <span id="{}_entryTitle" style="font-weight: bold;"> </span>
            <span id="{}_entryText" style=""> </span>
        </div>
        """,
        name, name);
    return html



"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
HTML CUSTOM ACCESSOR
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


@register.simple_tag
def ctrl_button(name, label, typeSubmit=False):
    html = format_html("""
        <div class="inner_margin2">
            <input id="{}_button" type="{}" value="{}"  
                class="format_button" style="">
            </input>
        </div>
        """,
        name,
        "button"   if not typeSubmit   else "submit",
        label);
    return html


@register.simple_tag
def ctrl_select(name, label):
    html = format_html("""
        <div class="display_cellM">
            <span class="inner_margin2" style="white-space: nowrap;">{}:</span>
        </div>
        <div class="display_cellM">
            <select id="{}_select" class="inner_margin2 format_cpointer"
                style="color: black;">
            </select>
        </div>
        """,
        label, name)
    return html


@register.simple_tag
def ctrl_input(name, label, extend=False):
    html = format_html("""
        <div class="display_cellM">
            <span class="inner_margin2" style="white-space: nowrap;">{}: </span>
        </div>
        <div class="display_cellM" style="{}">
            <input id="{}_input" type="text" maxlength="100" size="5"
                class="inner_margin2" style="overflow: hidden; color: black; {}"> </input>
        </div>""",
        label,
        "width: 100%;" if not extend  else "width: 100%;",
        name,
        "" if not extend  else "width: 96%; box-sizing: border-box; -webkit-box-sizing:border-box; -moz-box-sizing: border-box;",
        )
    return html


@register.simple_tag
def ctrl_table(name, center=False, fullWidth=False, title=""):
    html = format_html("""
        <div class="inner_margin2" style="display: block;">
            <span style="margin-bottom: 4px; display: block; font-weight: bold;">{}</span>
            <table id="{}_table" class="row-border" 
                style="{} margin: {} padding-top: 2px; 
                border: 1px solid black; background: white; color: black;">
            </table>
        </div>
        """,
        title,
        name,
        "width: auto !important;"  if not fullWidth  else "",
        "0 !important;"  if not center  else "0px auto;",
        );
    return html


@register.simple_tag
def ctrl_tableDeluxe(name):
    html = format_html("""
        <div class="display_block inner_margin2 format_frame">
            <div style="background: white; padding: 6px;">
                <table id="{}_table" class="format_full row-border"
                    style="color: black;"></table>
            </div>
        </div>
        """,
        name,
        );
    return html


@register.simple_tag
def ctrl_radio(p_name, p_options = []):
    html = format_html("""
        <div class="inner_margin2" style="margin-bottom: 0px;">
        """)
    for opt in p_options:
        html += format_html("""
            <input type="radio" name={} value={}
                id={}_{} class="" style="margin:0px; cursor: pointer;"></input>
            <label for="{}_{}" style="position: relative; top: -3px; cursor: pointer;" > {} </label> <br>
            """,
            p_name, opt.replace(" ", ""),
            p_name, opt.replace(" ", ""),
            p_name, opt.replace(" ", ""), opt)
    html += format_html("""
        </div>
        """)
    return html


@register.simple_tag
def ctrl_radioHoriz(p_name, p_options = []):
    html = format_html("""
        <div class="inner_margin2" style="margin-bottom: 0px;">
        """)
    for opt in p_options:
        html += format_html("""
            <input type="radio" name={} value={}
                id={}_{} class="" style="margin: 0px; cursor: pointer;"></input>
            <label for="{}_{}" class="format_fixline"
                style="position: relative; top: -3px; cursor: pointer;" > {} </label>
                &emsp;
            """,
            p_name, opt.replace(" ", ""),
            p_name, opt.replace(" ", ""),
            p_name, opt.replace(" ", ""), opt)
    html += format_html("""
        </div>
        """)
    return html


@register.simple_tag
def ctrl_checkbox(p_name, p_label):
    html = format_html("""
        <div class="inner_margin2" style="">
            <input id={}_checkbox type="checkbox" class="" 
                style="">{}</input>
        </div>""",
        p_name, p_label);
    return html


@register.simple_tag
def ctrl_datepicker(name, label):
    html = format_html("""
        <div class="display_cellM">
            <span class="inner_margin2" style="white-space: nowrap;">{}: </span>
        </div>
        <div class="display_cellM">
            <input id="{}_datepicker" type="text" 
                class="inner_margin2 format_center" style="width: 110px; color: black;"> 
        </div>""",
        label, name, )
    return html



@register.simple_tag
def ctrl_image(name, cssClass="", source=""):
    # send in: image_actualSize, image_smallSize, format_frame
    html = format_html("""
        <div class="format_center">
            <div class="inner_margin2">
               <img id="{}_image" class="{}" src="{}"> </img>
            </div>
        </div>""",
        name, cssClass, source);
    return html


@register.simple_tag
def ctrl_imageIcon(p_name, p_border=True):
    html = format_html("""
        <div style="height: 50px; width: 50px; margin: auto;
                position: relative; {} background-color: white; " >
            <img id="{}_image" src=""
                style="max-height: 100%; max-width: 100%;
                    position: absolute; margin: auto; top: 0; left: 0; right: 0; bottom: 0;"> </img>
        </div>""",
        "border: 1px solid black;"   if p_border   else "",
        p_name, );
    return html


@register.simple_tag
def ctrl_iconAwesome(name, icon, color="black"):
    html = format_html("""
        <div class="inner_margin2 icon_button">
            <i id="{}_icon" class="fa {} fa-lg" style="color: {};"></i>
        </div>
        """,
        name, icon, color);
    return html


@register.simple_tag
def ctrl_plot(name, style="height: 400px;"):
    html = format_html("""
        <div class="display_block inner_margin2 format_outline outer_padding1" style="background: white;">
            <div id="{}_plot" class="" style="{}">
            </div>
        </div>""",
        name, style);
    return html



"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
APP SPECIFIC
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


@register.simple_tag
def format_url(p_url, p_label):
    # used in email body
    html = format_html("""
        <a href="{}">{}</a> 
        """,
        str(p_url), p_label);
    return html





"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
END OF FILE
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""