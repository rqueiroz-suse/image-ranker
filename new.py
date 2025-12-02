import FreeSimpleGUI as sg
import os
import io
import random
import csv
from PIL import Image


class ImageRanker:
    def __init__(self):
        self.image_files = []
        self.folder_path = None
        self.rankings = {}
        self.current_left = None
        self.current_right = None


    def select_folder(self):

        folder = sg.popup_get_folder('Image folder to open', default_path='./images')

        if not folder:
            sg.popup_cancel('Cancelling')
            raise SystemExit()

        self.folder_path = folder
        self.load_images()
        return len(self.image_files) >= 2
        # create sub list of image files (no sub folders, no wrong file types)
        

    def load_images(self): 
        if not self.folder_path:
            return
        # PIL supported image types
        img_types = (".png", ".jpg", "jpeg", ".tiff", ".bmp")
        self.image_files = [
            f for f in os.listdir(self.folder_path) 
            if f.lower().endswith(img_types)
        ]
        
        self.rankings = {img: 0 for img in self.image_files}


    def convert_to_bytes(self, file_path, maxsize=(720, 480)):
        """Generate image data using PIL
        """
        # if not isinstance(file_path, (str, os.PathLike)):
        #     raise TypeError(f"Expected a path, got {type(file_path)}")
        # if not os.path.exists(file_path):
        #     raise FileNotFoundError(f"Image file not found: {file_path}")
        try:
            img = Image.open(file_path)
            img.thumbnail(maxsize)
            
            bio = io.BytesIO()
            img.save(bio, format="PNG")
            del img
            return bio.getvalue()
        except Exception as e:
            sg.popup_error(f"Error loading image: {e}")
            return None


    def get_random_image(self, exclude=None):
        available = [img for img in self.image_files if img != exclude]
        if not available:
            return None
        return random.choice(available)


    def update_images(self, keep_selected=None, new_random=None):
        if keep_selected is None:
            self.current_left, self.current_right = random.sample(self.image_files, 2)
        else:
            if keep_selected == 'left':
                self.current_left = self.current_left
                self.current_right = new_random if new_random else self.get_random_image(self.current_left)
            else:
                self.current_right = self.current_right
                self.current_left = new_random if new_random else self.get_random_image(self.current_right)

        return True


    def record_selection(self, selected_side):
        if selected_side == 'left':
            selected_image = self.current_left
        else:
            selected_image = self.current_right
        
        if selected_image:
            if selected_image not in self.rankings:
                self.rankings[selected_image] = 0
            self.rankings[selected_image] += 1
    

    def get_ranking_display(self):
        sorted_rankings = sorted(
            self.rankings.items(),
            key=lambda x: x[1],
            reverse=True
        )

        if not sorted_rankings:
            return "Empty ranking"
        
        max_filename_len = max(len(img) for img, _ in sorted_rankings) if sorted_rankings else 30
        max_filename_len = max(max_filename_len, 20)

        lines = [f"{'Image Filename':<{max_filename_len}} | Votes", "-" * (max_filename_len + 20)]
        
        for rank, (image, votes) in enumerate(sorted_rankings, 1):
            lines.append(f"{image:<{max_filename_len}} | {votes}")
        
        return "\n".join(lines)
    

    def get_ranking_table_data(self):
        sorted_rankings = sorted(
            self.rankings.items(),
            key=lambda x: x[1],
            reverse=True
        )

        table_data = []
        
        for rank, (image, votes) in enumerate(sorted_rankings, 1):
            table_data.append([rank, image, votes])
        
        return table_data


    def generate_rank_csv(self, header, data):
        filename = 'rank.csv'

        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(header)
            writer.writerows(data[0:])

        sg.popup_ok('CSV created successfully!')


    def run(self):

        ranking_header = ['rank', 'image_name', 'votes']

        if not self.select_folder():
            sg.popup_error('Please select a valid folder')
            return
        
        layout = [
            [
                sg.Column([
                    [sg.Image(key='-IMAGE1-', size=(720, 480), enable_events=True)]
                ], element_justification='center'),
                sg.VSeparator(),
                sg.Column([
                    [sg.Image(key='-IMAGE2-', size=(720, 480), enable_events=True)]
                ], element_justification='center')
            ],
            [sg.HorizontalSeparator()],
            [
                sg.Button('Rankings', key='-RANKINGS-'),
                sg.Button('Export ranking to CSV', key='-EXPORT_CSV-'),
                sg.Button('Exit App', key='-EXIT-')
            ],
            [sg.Text('Current Ranking:')],
            [
                sg.Table(
                    values=[],
                    headings=ranking_header,
                    key='-RANK_TABLE-',
                    auto_size_columns=True,
                    num_rows=10,
                    expand_x=True,
                    expand_y=False
                )
            ] 
        ]

        window = sg.Window('Image Ranker', layout, finalize=True, resizable=True)

        if not self.update_images():
            sg.popup_error("Any images were found!")
            window.close()
            return
        
        img1_path = os.path.join(self.folder_path, self.current_left)
        img2_path = os.path.join(self.folder_path, self.current_right)
        img1_data = self.convert_to_bytes(img1_path)
        img2_data = self.convert_to_bytes(img2_path)
        window['-IMAGE1-'].update(data=img1_data)
        window['-IMAGE2-'].update(data=img2_data)

        window['-RANK_TABLE-'].update(values=self.get_ranking_table_data())

        while True:
            event, values = window.read()

            if event in (sg.WIN_CLOSED, '-EXIT-'):
                break
            elif event == '-IMAGE1-':
                self.record_selection('left')
                new_img = self.get_random_image(self.current_left)
                if new_img:
                    self.update_images(keep_selected='left', new_random=new_img)
                    img1_path = os.path.join(self.folder_path, self.current_left)
                    img2_path = os.path.join(self.folder_path, self.current_right)
                    img1_data = self.convert_to_bytes(img1_path)
                    img2_data = self.convert_to_bytes(img2_path)
                    window['-IMAGE1-'].update(data=img1_data)
                    window['-IMAGE2-'].update(data=img2_data)
                    window['-RANK_TABLE-'].update(values=self.get_ranking_table_data())
            elif event == '-IMAGE2-':
                self.record_selection('right')
                new_img = self.get_random_image(self.current_right)
                if new_img:
                    self.update_images(keep_selected='right', new_random=new_img)
                    img1_path = os.path.join(self.folder_path, self.current_left)
                    img2_path = os.path.join(self.folder_path, self.current_right)
                    img1_data = self.convert_to_bytes(img1_path)
                    img2_data = self.convert_to_bytes(img2_path)
                    window['-IMAGE1-'].update(data=img1_data)
                    window['-IMAGE2-'].update(data=img2_data)
                    window['-RANK_TABLE-'].update(values=self.get_ranking_table_data())
            elif event == '-RANKINGS-':
                window['-RANK_TABLE-'].update(values=self.get_ranking_table_data())
            elif event == '-EXPORT_CSV-':
                window['-RANK_TABLE-'].update(values=self.get_ranking_table_data())
                self.generate_rank_csv(ranking_header, self.get_ranking_table_data())

        window.close()


def main():
    app = ImageRanker()
    app.run()


if __name__ == '__main__':
    main()
