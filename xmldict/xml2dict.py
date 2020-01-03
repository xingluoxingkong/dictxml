try:
    import xml.etree.ElementTree as ET
except:
    import cElementTree as ET

__all__ = ['XML2Dict']


class XML2Dict(object):
    def __init__(self, coding='UTF-8'):
        ''' XML转dict
        --
        '''
        self.coding = coding
        self.schemaLocation = ''

    def _make_child(self, node, children):
        for child in children:
            ctag = child.tag
            if ctag in node:    # 已经存在的，组成数组
                ctag1 = node.pop(ctag)
                ctag2 = self._make_dict(child)
                ctags = [ctag1, ctag2]
                node[ctag + '_all'] = ctags
            elif ctag + '_all' in node:    # 数组存在的，继续添加
                node[ctag + '_all'].append(self._make_dict(child))
            else:
                node[ctag] = self._make_dict(child)

    def _make_dict(self, node):
        tag = node.tag

        text = node.text.strip().encode(self.coding).decode(
            self.coding) if node.text is not None else ''

        children = list(node)

        attrib = {}
        if node.attrib:
            for k, v in node.attrib.items():
                if 'schemaLocation' in k:
                    self.schemaLocation =  '{' + v.split(' ')[0] + '}' 
                attrib[k] = v

        nodeDict = {}

        if text and not attrib and not children:
            nodeDict = text
        else:
            if attrib:
                nodeDict = attrib
            if children:
                self._make_child(nodeDict, children)
            if text:
                nodeDict['text'] = text

        return nodeDict

    def parse(self, xmlStr):
        ''' 转换xml字符串
        --
            @param xmlStr: 带转换的xml，字符串格式
        '''
        EL = ET.fromstring(xmlStr)

        res = {EL.tag: self._make_dict(EL)}
        return self.decodeBytes(res)

    def decodeBytes(self, res):
        ''' 编码解析出来的数据
        --
        '''
        res2 = {}
        for k, v in res.items():
            if isinstance(v, bytes):
                res[k] = v.decode(self.coding)
            if isinstance(v, list) or isinstance(v, dict) or isinstance(v, tuple):
                res[k] = self.decodeBytes(v)
            if '{' in k and '}' in k:
                endNum = k.find('}')
                k2 = k[endNum + 1:]
                res2[k2] = res[k]
        if self.schemaLocation:
            return res2
        return res
