import os

from PIL import Image


class ChartSplitter:
    def __init__(self):
        self.songTitle = None
        self.songLevel = None

    def split(self, songTitle: str, songLevel: str):
        self.songTitle = songTitle
        self.songLevel = songLevel

        output_dir = os.path.join('output', f'{self.songTitle}_{self.songLevel}')
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, f'all.png')

        img: Image = Image.open(file_path)
        w, h = img.size
        canvas: Image = Image.new('RGBA', (w, h))
        canvas.paste(img, (0, 0))

        split_top_y: list[int] = list()
        split_bottom_y: list[int] = list()
        for y in range(h):
            color: tuple[int, ...] = img.getpixel((0, y))
            if color[0] == 255 and color[1] == 0 and color[2] == 255:
                split_top_y.append(y)
            elif color[0] == 0 and color[1] == 255 and color[2] == 255:
                split_bottom_y.append(y)
            canvas.putpixel((0, y), img.getpixel((1, y)))

        if len(split_top_y) != len(split_bottom_y):
            raise Exception('array length is not same')

        split_top_y.reverse()
        split_bottom_y.reverse()

        if self.songLevel == '0':
            step = 6
        elif self.songLevel == '1':
            step = 4
        else:
            step = 2
        end = False
        idx = 0
        for i in range(len(split_top_y)):
            if i % step != 0:
                continue

            if i + step >= len(split_top_y):
                end = True
                top_y = split_top_y[-1]
                bottom_y = split_bottom_y[i]
            else:
                top_y = split_top_y[i+step]
                bottom_y = split_bottom_y[i]

            from_y = top_y
            to_y = bottom_y

            cropped = canvas.crop((0, from_y, w, to_y))

            cropped.save(os.path.join(output_dir, f'{str(idx).zfill(2)}.png'))
            idx += 1

            if end:
                break

    def merge(self):
        CHART_LIST: list[Image] = list()
        output_dir = os.path.join('output', f'{self.songTitle}_{self.songLevel}')

        files = os.listdir(output_dir)
        files.remove('all.png')
        if 'merged.png' in files:
            files.remove('merged.png')

        for file in files:
            img = Image.open(os.path.join(output_dir, file))
            CHART_LIST.append(img)

        width = CHART_LIST[0].size[0]
        height = CHART_LIST[0].size[1]
        CHART_MARGIN = 30
        MARGIN_LEFT = 40
        MARGIN_BOTTOM = 30

        CANVAS_WIDTH = (width * len(CHART_LIST)) + (CHART_MARGIN * (len(CHART_LIST) - 1))
        CANVAS_WIDTH += (MARGIN_LEFT * 2)
        CANVAS_HEIGHT = height + (MARGIN_BOTTOM * 2)

        canvas = Image.new('RGB', (CANVAS_WIDTH, CANVAS_HEIGHT), '#000000')

        x = MARGIN_LEFT
        for chart in CHART_LIST:
            if chart.size[1] < height:
                y = MARGIN_BOTTOM + (height - chart.size[1])
            else:
                y = MARGIN_BOTTOM
            canvas.paste(chart, (x, y))
            x += width + CHART_MARGIN

        # canvas.show()
        canvas.save(os.path.join(output_dir, 'merged.png'))


if __name__ == '__main__':
    for title in ['AfterSchoolDessert', 'Aoharu', 'BluemarkCanvas', 'IrodoriCanvas']:
        for level in range(3):
            print(f'{title} {level} Splitting...')
            sp = ChartSplitter()
            sp.split(title, str(level))
            sp.merge()
