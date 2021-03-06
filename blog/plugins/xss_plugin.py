


def filter_xss(html_str):
    #安全标签
    valid_tag_list = ["p", "hr","div", "a", "img", "html", "body", "br", "strong", "b","sub","sup","em"]
    #不安全属性
    valid_dict = {"p": ["id", "class"], "div": ["id", "class"]}

    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html_str, "html.parser")  # soup  ----->  document

    ######### 改成dict
    for ele in soup.find_all():
        # 过滤非法标签
        if ele.name not in valid_tag_list:
            ele.decompose()
        # 过滤非法属性

        else:
            attrs = ele.attrs  # p {"id":12,"class":"d1","egon":"dog"}
            l = []
            for k in attrs:
                if k not in valid_dict[ele.name]:
                    l.append(k)

            for i in l:
                del attrs[i]

    print(soup)

    return soup.decode()