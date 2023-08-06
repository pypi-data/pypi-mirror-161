

class CalculatePixelDistanceTool(object):
    def __init__(self,
                 video_path: str=None,
                 known_mm_distance: float=None):

        self.video_path = video_path
        self.video_dir, self.video_name, self.video_ext = get_fn_ext(video_path)
        if not os.access(video_path, os.R_OK):
            print('{} is not readable.'.format(video_path))
            raise FileNotFoundError

        self.video_meta_data = get_video_meta_data(self.video_path)
        print(self.video_meta_data)
        self.cap = cv2.VideoCapture(video_path)
        self.cap.set(1, 0)
        _, self.frame = self.cap.read()
        self.original_img = deepcopy(self.frame)
        max_res = max(self.video_meta_data['width'], self.video_meta_data['height'])
        space_scaler, radius_scaler, resolution_scaler, font_scaler = 80, 20, 1500, 1.5
        self.circle_scale = int(radius_scaler / (resolution_scaler / max_res))
        self.font_scale = float(font_scaler / (resolution_scaler / max_res))
        self.spacing_scale = int(font_scaler / (resolution_scaler / max_res))
        self.display_original_window()
        #self.display_modify_window()

    def create_instructions_window(self):
        self.side_img = np.ones((int(self.video_meta_data['height'] / 2), self.video_meta_data['width'], 3))
        cv2.putText(self.side_img, 'Double left mouse click on the first coordinate location.', (10, self.spacing_scale + 50), cv2.FONT_HERSHEY_SIMPLEX, self.font_scale, (10, 255, 10), 3)
        self.frame = np.uint8(np.concatenate((self.frame, self.side_img), axis=0))

    def create_second_instructions_window(self):
        self.side_img = np.ones((int(self.video_meta_data['height'] / 2), self.video_meta_data['width'], 3))
        cv2.putText(self.side_img, 'Double left mouse click on the second coordinate location.', (10, self.spacing_scale + 50), cv2.FONT_HERSHEY_SIMPLEX, self.font_scale, (10, 255, 10), 3)
        self.frame = np.uint8(np.concatenate((self.frame, self.side_img), axis=0))

    def display_original_window(self):
        coordinate_lst = []
        cv2.namedWindow('SELECT_COORDINATES: double left mouse click at two locations. Press ESC when done', cv2.WINDOW_NORMAL)
        def draw_circle(event, x, y, flags, param):
            if (event == cv2.EVENT_LBUTTONDBLCLK):
                cv2.circle(self.frame, (x, y), self.circle_scale, (144, 0, 255), -1)
                coordinate_lst.append((x,y))

        self.create_first_instructions_window()
        while True:
            cv2.setMouseCallback('SELECT_COORDINATES: double left mouse click at two locations. Press ESC when done', draw_circle)
            cv2.imshow('SELECT_COORDINATES: double left mouse click at two locations. Press ESC when done', self.frame)
            k = cv2.waitKey(20) & 0xFF
            if (k == 27) or (len(coordinate_lst) == 1):
                break

        self.create_second_instructions_window()

    # cv2.line(self.frame, (coordinate_lst[0][0], coordinate_lst[0][1]), (coordinate_lst[1][0], coordinate_lst[1][1]), (144, 0, 255), self.circle_scale)
    # cv2.imshow('SELECT_COORDINATES: double left mouse click at two locations. Press ESC when done', self.frame)

    #def display_modify_window(self):

# test = CalculatePixelDistanceTool(video_path='/Users/simon/Desktop/troubleshooting/train_model_project/project_folder/videos/Together_1.avi', known_mm_distance=22)
#
#
