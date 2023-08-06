# encoding: utf-8
from . import sx
#pip install python-docx==0.8.11
from docx import Document
from docx.shared import Cm,Pt
import base64
from PIL import Image
from io import BytesIO
class 试题():
    题目=解析=选项=答案=题型=''
    题目图片=解析图片=[]
    def __str__(self):
        s='''{}\n{}{}\n{}\n{}\n{}\n'''.format(self.题目,
                                              '图片:' + str(self.题目图片)+'\n' if self.题目图片 else '',
                                              self.选项,
                                              self.答案,
                                              self.解析,
                                              '图片:' + str(self.解析图片)+'\n' if self.解析图片 else '')
        return s
def 解析试题到文档(st:试题, 段落, 过滤字符列表:list=['\x08', '\x07'],题目图片尺寸:float=10,解析图片尺寸:float=10)->None:
    '''
    :param st:试题对象
    :param 段落: doc = document.add_paragraph('')  # 添加段落
    :return:
    '''
    def add_row(s:str):
        assert isinstance(s,str),'非文本对象,无法写入到文档'
        for x in 过滤字符列表:
            s = s.replace(x, '')
        段落.add_run(f'{s}\n')
    add_row(sx.XPATH(st.题目).取文本())#去掉html标签
    if st.题目图片:
        for img_url in st.题目图片:
            try:
                pic = 段落.add_run()
                if 'data:image' in img_url:
                    img=sx.base64图片转PIL(img_url.strip())
                else:
                    img = sx.获取_网络图片(图片网址=img_url.strip(), pil=1)
                img.save('temp.png')
                pic.add_picture('temp.png', width=Cm(题目图片尺寸))
                段落.add_run('\n')
            except Exception as e:
                sx.打印错误(e)
    add_row(st.选项)
    add_row(st.答案)
    add_row(sx.XPATH(st.解析).取文本()) #去掉html标签
    if st.解析图片:
        for img_url in st.解析图片:
            try:
                pic = 段落.add_run()
                if 'data:image' in img_url:
                    img = sx.base64图片转PIL(img_url.strip())
                else:
                    img = sx.获取_网络图片(图片网址=img_url.strip(), pil=1)
                img.save('temp.png')
                pic.add_picture('temp.png', width=Cm(解析图片尺寸))
                段落.add_run('\n')
            except Exception as e:
                sx.打印错误(e)
    段落.add_run('\n')
if __name__ == '__main__':
    #使用实例
    document = Document()
    document.styles['Normal'].font.name = u'宋体'
    document.styles['Normal'].font.size = Pt(12)  # 小四
    p = document.add_paragraph('')  # 添加段落
    st=试题()
    st.题目='题目'
    st.解析='解析'
    st.选项='A.1\nB.2'
    st.答案='A'
    st.题型='选择题'
    st.解析图片=['http://ip.wgnms.top:9980/static/images/default.jpg']
    st.题目图片=['http://ip.wgnms.top:9980/static/images/default.jpg']
    print(st)
    解析试题到文档(st,p)
    document.save('abc.docx')