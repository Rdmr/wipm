import  wx
import  wx.stc  as  stc
import PySTC
import pmImgCreator
from SerialConnection import SerialConnection

MAX_OBJ_SIZE = 2048
SERIALRX = wx.NewEventType()
# bind to serial data receive events
EVT_SERIALRX = wx.PyEventBinder(SERIALRX, 0)


        
class MySTC(PySTC.MySTC):
    def __init__(self, parent, parentFrame):
        PySTC.MySTC.__init__(self, parent)
        self.markers = [self.MarkerAdd(0,0)]
        self.parentFrame = parentFrame

        #Line numbers
        self.SetMarginType(1, wx.stc.STC_MARGIN_NUMBER)
        self.SetMarginWidth(1, 40)
        
        #Zooming
        self.CmdKeyAssign(ord('+'),stc.STC_SCMOD_ALT,stc.STC_CMD_ZOOMIN)
        self.CmdKeyAssign(ord('-'),stc.STC_SCMOD_ALT,stc.STC_CMD_ZOOMOUT)
        
        # Bind
        self.Bind(wx.EVT_KEY_UP, self.onKeyUp)
        self.Bind(stc.EVT_STC_CHANGE, self.onChange, self)
        
        #        
        self.Changed = False
        self.SetEOLMode(stc.STC_EOL_LF)
        self.SetUseTabs(False)
        
    def onChange(self, event):
        self.Changed = True
        
    def onKeyUp(self, event):
        key = event.GetKeyCode()
        if key in (wx.WXK_NUMPAD_ENTER, wx.WXK_RETURN):
            self.Autoindent()

    def Autoindent(self):
        prev_lineN = self.GetCurrentLine()-1
        prev_str = self.GetLine(prev_lineN).rstrip()
        indent = self.GetLineIndentation(prev_lineN)
        if (len(prev_str) > 4) and (prev_str[-1] == ':'):
            indent += 4
        
        if (prev_str.startswith('return') or prev_str.startswith('pass')):
           indent -= 4
        if (indent < 0): intend = 0
    
        cur = self.GetCurrentPos()
        self.InsertText(cur, ' '*indent)
        cur += indent
        self.SetCurrentPos(cur)
        self.SetSelection(cur, cur)
        
        if (indent == 0):
            beg = self.MarkerLineFromHandle(self.markers[-1])
            end = self.GetLineCount()
            src = ''.join([self.GetLine(i) for i in xrange(beg, end)]).rstrip()
            self.ipm(src)
            self.markers.append(self.MarkerAdd(self.GetCurrentLine(),3))
 
    def ipm(self, src):
        pmfeatures = pmImgCreator.PmImgCreator(self.parentFrame.cfg.get('MAIN','PMFEATURES') + "/pmfeatures.py")
        try:
            code = compile(src, '', 'single')
        except Exception, e:
            self.AppendText('> ' + "%s:%s\n" % (e.__class__.__name__, e) + '\n')
            self.DocumentEnd()
            return
                
        img = pmfeatures.co_to_str(code)
        if len(img) > MAX_OBJ_SIZE:
            self.AppendText('> ' +  "Error: object is too big. It must be less than " + MAX_OBJ_SIZE +" bytes. " + str(len(img)) + " bytes now.\n")
            self.DocumentEnd()
            return
        port = self.parentFrame.cfg.get('SERIAL','port')
        baud = self.parentFrame.cfg.get('SERIAL','baudrate')
        conn = SerialConnection(port,baud)
        conn.write(img)
        self.AppendText(">")
        prev = ''
        for c in conn.read():
            if prev == '\n': self.AppendText(">")
            self.AppendText(c)
            wx.Yield()
            prev = c
        
        conn.close()    
        self.AppendText("\n")
        self.DocumentEnd()
       