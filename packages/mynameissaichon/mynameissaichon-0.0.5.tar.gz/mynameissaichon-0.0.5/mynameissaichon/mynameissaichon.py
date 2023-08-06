import random
class Saichon:

    """
    Class Saichon คือ
    ข้อมูลที่เกี่ยวกับ สายชล
    ประกอบด้วยชื่อเพจ
    ชื่อช่องยูทูป
    """
    def __init__(self):
        self.name = 'สายชล'
        self.page = 'https://www.facebook.com/Ymingt/'

    def show_name(self):
        print(f'สวัสดีฉันชื่อ {self.name}')

    def show_youtube(self):
        print('https://www.youtube.com/channel/UCm7tUVUjzsYX3hNsjr44ewA')

    def about(self):
        text = """
        -----------------------------------
        สวัสดีครับผมเป็น Air Engineer กำลังเรียนรู้เกี่ยวกับ python
        อยู่ระหว่างฝึกฝนครับ
        ----------------------------------
        """
        print(text)

    def show_atr(self):
        text = """
        Art by David Palmer
                                               .--.
                                               `.  \\
                                                 \  \\
                                                  .  \\
                                                  :   .
                                                  |    .
                                                  |    :
                                                  |    |
  ..._  ___                                       |    |
 `."".`''''""--..___                              |    |
 ,-\  \             ""-...__         _____________/    |
 / ` " '                    `""''''''                   .
 \                                                      L
 (>                                                      \\
/                                                         \\
\_    ___..---.                                            L
  `--'         '.                                           \\
                 .                                           \_
                _/`.                                           `.._
             .'     -.                                             `.
            /     __.-Y     /''''''-...___,...--------.._            |
           /   _."    |    /                ' .      \   '---..._    |
          /   /      /    /                _,. '    ,/           |   |
          \_,'     _.'   /              /''     _,-'            _|   |
                  '     /               `-----''               /     |
                  `...-'                                       `...-'
        """
        print(text)

    def dice(self):
        dice_list = ['⚀','⚁','⚂','⚃','⚄','⚅']
        first = random.choice(dice_list)
        second = random.choice(dice_list)
        print(f'คุณทอยเต๋าได้ {first}{second}')

'''if __name__ == '__main__':
    chon = Saichon()
    chon.show_name()
    chon.show_youtube()
    chon.about()
    chon.show_atr()
    chon.dice()'''