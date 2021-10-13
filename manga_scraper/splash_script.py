LIST_CHAPTER = """
function wait_for_element(splash, css, maxwait)
    -- Wait until a selector matches an element
    -- in the page. Return an error if waited more
    -- than maxwait seconds.
    if maxwait == nil then
        maxwait = 10
    end
    return splash:wait_for_resume(string.format([[
        function main(splash) {
            var selector = '%s';
            var maxwait = %s;
            var end = Date.now() + maxwait*1000;

            function check() {
                if(document.getElementsByClassName("selector")) {
                    splash.resume('Element found');
                } else if(Date.now() >= end) {
                    var err = 'Timeout waiting for element';
                    splash.error(err + " " + selector);
                } else {
                    setTimeout(check, 200);
                }
            }
            check();
        }
    ]], css, maxwait))
end

function main(splash, args)
    splash:go(splash.args.url)
    wait_for_element(splash, "scroll-area", 30)
    
    local js_scroll = string.format([[
        var scroll_area = document.getElementsByClassName("scroll-area")[0];     
        scroll_area.scrollTop = scroll_area.scrollHeight;
        ]])
    
    assert(splash:wait(10))

    local sa = splash:select('.scroll-area')
    local sa_t = sa.scrollTop 
    local sa_y = -1
        
    while ( sa_y < sa_t ) 
    do
        sa_y = sa_t

        splash:runjs(js_scroll)
        splash:wait(1)
        sa = splash:select('.scroll-area')
        sa_t = sa.scrollTop
    end
    
    assert(splash:wait(5))
    
    return {
        html = splash:html(),
        }
end
"""

OPEN_CHAPTER = """
function main(splash, args)
  assert(splash:go(args.url))
  assert(splash:wait(5))
  return {
    html = splash:html(),
  }
end
"""
