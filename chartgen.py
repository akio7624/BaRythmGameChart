import copy
import os
from dataclasses import dataclass

from PIL import Image, ImageDraw, ImageFont
import json


class NoteData:
    noteType: str = None
    lane: int = None
    beat: int = None
    grid: int = None
    gridsPerBeat: int = None
    endBeat: int = None  # long note only
    endGrid: int = None  # long note only
    fever: bool = None

    def __init__(self, noteType, lane, beat, grid, gridsPerBeat, endBeat, endGrid, fever):
        self.noteType: str = noteType
        self.lane: int = lane
        self.beat: int = beat
        self.grid: int = grid
        self.gridsPerBeat: int = gridsPerBeat
        self.endBeat: int = endBeat
        self.endGrid: int = endGrid
        self.fever: bool = fever

        if self.noteType not in ['basic', 'long']:
            raise Exception(f"NoteType must be either 'basic' or 'long'. this is {noteType}")

    def get_note_type(self) -> str:
        return self.noteType

    def get_lane(self) -> int:
        return self.lane

    def get_beat(self) -> int:
        return self.beat

    def get_grid(self) -> int:
        return self.grid

    def get_gridsPerBeat(self) -> int:
        return self.gridsPerBeat

    def get_endBeat(self) -> int:
        return self.endBeat

    def get_endGrid(self) -> int:
        return self.endGrid

    def get_fever(self) -> bool:
        return self.fever


@dataclass
# draw params
class dp:
    PADDING_LEFT: int
    VERTICAL_OUTLINE_LEFT_WIDTH: int
    VERTICAL_OUTLINE_RIGHT_WIDTH: int
    PADDING_RIGHT: int
    PADDING_TOP: int
    HORIZONTAL_OUTLINE_TOP_WIDTH: int
    HORIZONTAL_OUTLINE_BOTTOM_WIDTH: int
    PADDING_BOTTOM: int
    LAIN_WIDTH: int
    LAIN_LINE_WIDTH: int
    VERTICAL_OUTLINE_COLOR: str
    HORIZONTAL_OUTLINE_COLOR: str
    LAIN_LINE_COLOR: str
    BAR_HEIGHT: int
    BAR_LINE_WIDTH: int
    BAR_LINE_COLOR: str
    BAR_COUNT: int
    BEAT_PER_BAR: int
    CANVAS_WIDTH: int
    CANVAS_HEIGHT: int
    DRAW_BEAT_LINE: bool
    DRAW_GRID_LINE: bool
    NOTE_IMG: dict[str, list[Image]]
    NOTE_HEIGHT: dict[str, int]


class ChartGenerator:
    title = None
    level = None
    RAW_NOTES: list[NoteData] = None
    noteData: dict[int, list[NoteData]] = None
    canvas: Image = None
    draw: ImageDraw = None
    font: ImageFont = None
    defaultGridsPerBeat = None

    def __init__(self):
        self.title = None
        self.level = None
        self.RAW_NOTES: list[NoteData] = list()
        self.noteData: dict[int, list[NoteData]] = dict()
        self.defaultGridsPerBeat = None

    def make(self, songTitle: str, songLevel: str):
        self.title = songTitle
        self.level = songLevel

        with open(f'json/{self.title}_{self.level}.json', 'r') as f:
            data = json.load(f)['data']

        self.defaultGridsPerBeat = data['gridsPerBeat']

        for note in data['notes']:
            self.RAW_NOTES.append(NoteData(
                note.get('type'),
                note.get('lane'),
                note.get('beat'),
                note.get('grid'),
                note.get('gridsPerBeat'),
                note.get('endBeat'),
                note.get('endGrid'),
                note.get('fever')
            ))

        self.initDrawParams()
        self.processNote()
        self.drawBackground()
        self.drawNotes()

        # self.canvas.show()

        output_dir = os.path.join('output', f'{self.title}_{self.level}')
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, f'all.png')
        print(f'Save image to {file_path}')
        self.canvas.save(file_path)

    def initDrawParams(self):
        PADDING_LEFT = 40
        VERTICAL_OUTLINE_LEFT_WIDTH = 2
        VERTICAL_OUTLINE_RIGHT_WIDTH = 2
        PADDING_RIGHT = 15

        PADDING_TOP = 20
        HORIZONTAL_OUTLINE_TOP_WIDTH = 3
        HORIZONTAL_OUTLINE_BOTTOM_WIDTH = 3
        PADDING_BOTTOM = 20

        LAIN_WIDTH = 70
        LAIN_LINE_WIDTH = 1
        
        VERTICAL_OUTLINE_COLOR = 'white'
        HORIZONTAL_OUTLINE_COLOR = 'white'
        LAIN_LINE_COLOR = 'white'

        if self.level == '0':
            BAR_HEIGHT = 240
        elif self.level == '1':
            BAR_HEIGHT = 720
        elif self.level == '2':
            BAR_HEIGHT = 1080
        else:
            raise Exception(f'Unknown level {self.level}')

        BAR_COUNT_LIST = {
            'AfterSchoolDessert': 82,
            'Aoharu': 91,
            'BluemarkCanvas': 100,
            'IrodoriCanvas': 117,
        }

        BAR_LINE_WIDTH = 3
        BAR_LINE_COLOR = 'white'
        BAR_COUNT = BAR_COUNT_LIST[self.title]
        BEAT_PER_BAR = 4

        CANVAS_WIDTH = PADDING_LEFT + VERTICAL_OUTLINE_LEFT_WIDTH + (LAIN_WIDTH * 4) + (LAIN_LINE_WIDTH * 3) + VERTICAL_OUTLINE_RIGHT_WIDTH + PADDING_RIGHT
        CANVAS_HEIGHT = PADDING_BOTTOM + 1 + PADDING_TOP + 1

        for i in range(BAR_COUNT):
            CANVAS_HEIGHT += BAR_HEIGHT
            CANVAS_HEIGHT += BAR_LINE_WIDTH

        NOTE_IMG = {
            'basic': [],
            'long_start': [],
            'long': [],
            'long_end': [],
        }

        NOTE_HEIGHT = {
            'basic': 0,
            'long_start': 0,
            'long': 0,
            'long_end': 0,
        }

        for note_type in ['basic', 'long_start', 'long', 'long_end']:
            for i in range(5):
                if i == 4:
                    i = 'fever'
                img = Image.open(f'imgs/{note_type}_lane_{i}.png').convert('RGBA')
                original_w, original_h = img.size
                new_height = int((LAIN_WIDTH / original_w) * original_h)
                NOTE_IMG[note_type].append(img.resize((LAIN_WIDTH, new_height), Image.Resampling.LANCZOS))
                NOTE_HEIGHT[note_type] = new_height

        self.font = ImageFont.truetype(r'Freesentation-7Bold.ttf', 20)
        self.canvas = Image.new('RGB', (CANVAS_WIDTH, CANVAS_HEIGHT), '#2e2e2e')
        self.draw = ImageDraw.Draw(self.canvas)

        dp.PADDING_LEFT = PADDING_LEFT
        dp.VERTICAL_OUTLINE_LEFT_WIDTH = VERTICAL_OUTLINE_LEFT_WIDTH
        dp.VERTICAL_OUTLINE_RIGHT_WIDTH = VERTICAL_OUTLINE_RIGHT_WIDTH
        dp.PADDING_RIGHT = PADDING_RIGHT
        dp.PADDING_TOP = PADDING_TOP
        dp.HORIZONTAL_OUTLINE_TOP_WIDTH = HORIZONTAL_OUTLINE_TOP_WIDTH
        dp.HORIZONTAL_OUTLINE_BOTTOM_WIDTH = HORIZONTAL_OUTLINE_BOTTOM_WIDTH
        dp.PADDING_BOTTOM = PADDING_BOTTOM
        dp.LAIN_WIDTH = LAIN_WIDTH
        dp.LAIN_LINE_WIDTH = LAIN_LINE_WIDTH
        dp.VERTICAL_OUTLINE_COLOR = VERTICAL_OUTLINE_COLOR
        dp.HORIZONTAL_OUTLINE_COLOR = HORIZONTAL_OUTLINE_COLOR
        dp.LAIN_LINE_COLOR = LAIN_LINE_COLOR
        dp.BAR_HEIGHT = BAR_HEIGHT
        dp.BAR_LINE_WIDTH = BAR_LINE_WIDTH
        dp.BAR_LINE_COLOR = BAR_LINE_COLOR
        dp.BAR_COUNT = BAR_COUNT
        dp.BEAT_PER_BAR = BEAT_PER_BAR
        dp.CANVAS_WIDTH = CANVAS_WIDTH
        dp.CANVAS_HEIGHT = CANVAS_HEIGHT
        dp.NOTE_IMG = NOTE_IMG
        dp.NOTE_HEIGHT = NOTE_HEIGHT

        dp.DRAW_BEAT_LINE = True
        dp.DRAW_GRID_LINE = True

    def drawBackground(self):
        self.draw.line((dp.PADDING_LEFT, 0, dp.PADDING_LEFT, dp.CANVAS_HEIGHT), fill=dp.VERTICAL_OUTLINE_COLOR, width=dp.VERTICAL_OUTLINE_LEFT_WIDTH)

        # detail draw
        for beat in range(dp.BAR_COUNT * dp.BEAT_PER_BAR):
            if dp.DRAW_BEAT_LINE and beat % dp.BEAT_PER_BAR != 0:
                sx = self.get_x_from_lane(0)
                ex = self.get_x_from_lane(4) - dp.VERTICAL_OUTLINE_RIGHT_WIDTH
                y = self.get_y_from_beat(beat)
                self.draw.line((sx, y, ex, y), fill='white', width=1)

            if dp.DRAW_GRID_LINE:
                sx = self.get_x_from_lane(0)
                ex = self.get_x_from_lane(4) - dp.VERTICAL_OUTLINE_RIGHT_WIDTH
                gridPerBeats = self.defaultGridsPerBeat
                if beat in self.noteData:
                    max_gpb = self.noteData[beat][0].get_gridsPerBeat()
                    for note in self.noteData[beat]:
                        max_gpb = max(max_gpb, note.get_gridsPerBeat())
                    gridPerBeats = max_gpb
                    print(f'{beat}: {gridPerBeats}')
                for grid in range(gridPerBeats):
                    if grid == 0:
                        continue
                    y = self.get_y_from_beat(beat + 1) + self.get_height_from_grid(grid, gridPerBeats)
                    self.draw.line((sx, y, ex, y), fill='#777777', width=1)

        x = dp.PADDING_LEFT + dp.VERTICAL_OUTLINE_LEFT_WIDTH + dp.LAIN_WIDTH
        for i in range(3):
            self.draw.line((x, 0, x, dp.CANVAS_HEIGHT), fill=dp.LAIN_LINE_COLOR, width=dp.LAIN_LINE_WIDTH)
            x += dp.LAIN_LINE_WIDTH + dp.LAIN_WIDTH

        x = dp.CANVAS_WIDTH - dp.PADDING_RIGHT - dp.VERTICAL_OUTLINE_RIGHT_WIDTH
        self.draw.line((x, 0, x, dp.CANVAS_HEIGHT), fill=dp.VERTICAL_OUTLINE_COLOR, width=dp.VERTICAL_OUTLINE_RIGHT_WIDTH)

        self.draw.line((0, dp.CANVAS_HEIGHT - dp.PADDING_TOP, dp.CANVAS_WIDTH, dp.CANVAS_HEIGHT - dp.PADDING_TOP), fill=dp.HORIZONTAL_OUTLINE_COLOR, width=dp.HORIZONTAL_OUTLINE_BOTTOM_WIDTH)
        # self.draw.line((0, dp.PADDING_BOTTOM - 1, dp.CANVAS_WIDTH, dp.PADDING_BOTTOM - 1), fill=dp.HORIZONTAL_OUTLINE_COLOR, width=dp.HORIZONTAL_OUTLINE_TOP_WIDTH)

        y = dp.CANVAS_HEIGHT - dp.PADDING_TOP
        self.draw.point((0, y - 25), fill='#ff00ff')
        self.draw.point((0, dp.CANVAS_HEIGHT-1), fill='#00ffff')
        self.draw.text((dp.PADDING_LEFT - 30, y - 25), '01', font=self.font, fill='white')
        for i in range(dp.BAR_COUNT):
            if i + 1 != dp.BAR_COUNT:
                y -= dp.BAR_HEIGHT
                self.draw.line((10, y, dp.CANVAS_WIDTH - dp.PADDING_RIGHT - 1, y), fill=dp.BAR_LINE_COLOR, width=dp.BAR_LINE_WIDTH)
                self.draw.text((dp.PADDING_LEFT - 30, y - 25), str(i + 2).zfill(2), font=self.font, fill='white')
                self.draw.point((0, y - 25), fill='#ff00ff')
                self.draw.point((0, y + 15), fill='#00ffff')

    # gridPerBeats 최대 12 ..., 홀수도 존재
    def processNote(self):
        result = dict()

        for NOTE in self.RAW_NOTES:
            result.setdefault(NOTE.get_beat(), list())
            result[NOTE.get_beat()].append(NOTE)

        self.noteData = result

    def drawNotes(self):

        for BEAT, NOTES in self.noteData.items():
            for NOTE in NOTES:
                lane = NOTE.get_lane()
                grid = NOTE.get_grid()
                gridsPerBeat = NOTE.get_gridsPerBeat()
                fever = NOTE.get_fever()

                if NOTE.get_note_type() == 'basic':
                    x = self.get_x_from_lane(lane)
                    y = self.get_y_from_beat(BEAT) - self.get_height_from_grid(grid, gridsPerBeat)

                    self.draw_basic_note_image(x, y, lane, fever)
                else:  # long note
                    endBeat = NOTE.get_endBeat()
                    endGrid = NOTE.get_endGrid()

                    x1 = self.get_x_from_lane(lane)
                    y1 = self.get_y_from_beat(BEAT) - self.get_height_from_grid(grid, gridsPerBeat)

                    x2 = self.get_x_from_lane(lane)
                    y2 = self.get_y_from_beat(endBeat) - self.get_height_from_grid(endGrid, gridsPerBeat)

                    self.draw_long_note_image(x1, y1, x2, y2, lane, fever)

    def get_x_from_lane(self, lane: int) -> int:
        x = dp.PADDING_LEFT + dp.VERTICAL_OUTLINE_LEFT_WIDTH
        x += (dp.LAIN_WIDTH + dp.LAIN_LINE_WIDTH) * lane

        return x

    def get_y_from_beat(self, beat: int) -> int:
        HEIGHT_PER_BEAT = int(dp.BAR_HEIGHT / dp.BEAT_PER_BAR)
        y = dp.CANVAS_HEIGHT - dp.PADDING_BOTTOM
        y -= HEIGHT_PER_BEAT * beat

        return y

    def get_height_from_grid(self, grid: int, gridPerBeats: int) -> int:
        HEIGHT_PER_BEAT = int(dp.BAR_HEIGHT / dp.BEAT_PER_BAR)
        HEIGHT_PER_GRID = int(HEIGHT_PER_BEAT / gridPerBeats)
        h = 0
        h += HEIGHT_PER_GRID * grid

        return h

    def draw_basic_note_image(self, x: int, y: int, lane: int, fever: bool):
        if fever:
            lane = 4

        NOTE_IMG: Image = dp.NOTE_IMG['basic'][lane]
        NOTE_HEIGHT: int = dp.NOTE_HEIGHT['basic']

        y -= int(NOTE_HEIGHT / 2)

        self.canvas.paste(NOTE_IMG, (x, y), NOTE_IMG)

    def draw_long_note_image(self, x1: int, y1: int, x2: int, y2: int, lane: int, fever: bool):
        if fever:
            lane = 4

        if y1 <= y2:
            raise Exception(f'long note y error: y1(start y): {y1}   y2(end y): {y2}')

        NOTE_START_IMG: Image = dp.NOTE_IMG['long_start'][lane]
        NOTE_MIDDLE_IMG: Image = dp.NOTE_IMG['long'][lane]
        NOTE_END_IMG: Image = dp.NOTE_IMG['long_end'][lane]
        NOTE_END_HEIGHT: int = dp.NOTE_HEIGHT['long_end']

        y2 -= NOTE_END_HEIGHT

        MIDDLE_HEIGHT = y1 - y2
        long_w, _ = NOTE_MIDDLE_IMG.size
        RESIZED_MIDDLE = copy.deepcopy(NOTE_MIDDLE_IMG).resize((long_w, MIDDLE_HEIGHT), Image.Resampling.LANCZOS)

        self.canvas.paste(NOTE_START_IMG, (x1, y1), NOTE_START_IMG)
        self.canvas.paste(RESIZED_MIDDLE, (x2, y2), RESIZED_MIDDLE)
        self.canvas.paste(NOTE_END_IMG, (x2, y2), NOTE_END_IMG)


if __name__ == '__main__':
    for title in ['AfterSchoolDessert', 'Aoharu', 'BluemarkCanvas', 'IrodoriCanvas']:
        for level in range(3):
            print(f'{title} {level} Extracting...')
            ChartGenerator().make(title, str(level))
    # ChartGenerator().make('IrodoriCanvas', str(2))
