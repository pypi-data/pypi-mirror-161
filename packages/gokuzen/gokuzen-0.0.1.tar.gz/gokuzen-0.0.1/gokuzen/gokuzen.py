class gokuzen:
    """
    คลาส gokuzen คือ
    เป็นข้อมูลสำหรับการทดสอบ เรียน basic python กับ uncle engineer

    Example
    #-----------------------
    gokuzen = gokuzen()
    gokuzen.show_name()
    gokuzen.show_mail()
    gokuzen.about()
    gokuzen.show_ascii()
    #-----------------------
    """
    def __init__(self):
        self.name = 'gokuzen'
        self.mail = 'likit.tone@gmail.com'
    
    def show_name(self):
        print('สวัสดีฉันชื่อ {}'.format(self.name))

    def show_mail(self):
        print('mail ของเรา : gokuzen@gmail.com')
    
    def about(self):
        text = '''
        -------------------------------
        Gokusen มีที่มาจากสองคำ ก็คือ 
        - Gokudoumono มีความหมายว่า คนพาล 
        - Sensei มีความหมายว่า ครู. อาจารย์
        -------------------------------
        '''
        print(text)
    
    def show_ascii(self):
        text = '''
            _                      _______                      _
        _dMMMb._                .imgokuzen.                 _,dMMMb_
        dP'  ~YMMb            dOOOOOOOOOOOOOOOb            aMMP~  `Yb
        V      ~"Mb          dOOOOOOOOOOOOOOOOOb          dM"~      V
                `Mb.       dOOOOOOOOOOOOOOOOOOOb       ,dM'
                `YMb._   |OOOOOOOOOOOOOOOOOOOOO|   _,dMP'
            __     `YMMM| OP'~"YOOOOOOOOOOOP"~`YO |MMMP'     __
            ,dMMMb.     ~~' OO     `YOOOOOP'     OO `~~     ,dMMMb.
        _,dP~  `YMba_      OOb      `OOO'      dOO      _aMMP'  ~Yb._
                    `YMMMM\`OOOo     OOO     oOOO'/MMMMP'
            ,aa.     `~YMMb `OOOb._,dOOOb._,dOOO'dMMP~'       ,aa.
        ,dMYYMba._         `OOOOOOOOOOOOOOOOO'          _,adMYYMb.
        ,MP'   `YMMba._      OOOOOOOOOOOOOOOOO       _,adMMP'   `YM.
        MP'        ~YMMMba._ YOOOOPVVVVVYOOOOP  _,adMMMMP~       `YM
        YMb           ~YMMMM`OOOOI`````IOOOOO'MMMMP~           dMP
        `Mb.           `YMMMb`OOOI,,,,,IOOOO'dMMMP'           ,dM'
            `'                 `OObNNNNNdOO'                   `'
                                `~OOOOO~' 

        '''
        print(text)


if __name__ == '__main__':
    gokuzen = gokuzen()
    gokuzen.show_name()
    gokuzen.show_mail()
    gokuzen.about()
    gokuzen.show_ascii()