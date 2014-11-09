from uliweb import settings

def menu(path):
    menu_head = '<div id="sidebar-nav" class="hidden-phone"><ul id="dashboard-menu">'
    menu_end = '</ul></div>'
    menu_li = '<li%s <a href="%s"> <i class="%s"></i> <span>%s</span> </a> </li>'
    active = ' class="active"><div class="pointer"><div class="arrow"></div><div class="arrow_border"></div></div>'
    html = ''
    html += menu_head
    menus = settings.get_var('MENU/MenuList')
    for url,style,name in menus:
        if url == path:
            html +=(menu_li %(active,url,style,name))
        else:
            html += (menu_li %('>',url,style,name))
    html += menu_end
    return html