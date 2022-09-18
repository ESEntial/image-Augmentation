from symtable import Symbol
import cv2
import mediapipe as mp
import numpy as np
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_face_mesh = mp.solutions.face_mesh


# 이미지 파일의 경우을 사용하세요.:
IMAGE_FILES = ["C:/Users/happy/AppData/Local/Programs/Python/Python39/Git_Local/eunbin.jpg"]

# 표현되는 랜드마크의 굵기와 반경
drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=2)
mean = 0
oval = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378,
        400, 377, 152, 148, 176, 149, 150, 136, 172, 58, 132, 93, 234, 127, 162, 21,
        54, 103, 67, 109]

with mp_face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5) as face_mesh:
    for idx, file in enumerate(IMAGE_FILES):
        # 얼굴부분 crop 
        # haarcascade 불러오기
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        # 이미지 불러오기
        image = cv2.imread(file)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 얼굴 찾기        
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in faces:
            # cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cropped = image[y: y+h+100, x: x+w]
            resize = cv2.resize(cropped, (800, 900))
        image = resize
        
        # 작업 전에 BGR 이미지를 RGB로 변환합니다.
        results = face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        # 이미지에 출력하고 그 위에 얼굴 그물망 경계점을 그립니다.
        if not results.multi_face_landmarks:
            continue
        annotated_image = image.copy()
        ih, iw, ic = annotated_image.shape
        for face_landmarks in results.multi_face_landmarks:

            # 각 랜드마크를 image에 overlay 시켜줌
            mp_drawing.draw_landmarks(
                image=annotated_image,
                landmark_list=face_landmarks,
                connections=mp_face_mesh.FACEMESH_CONTOURS,
                landmark_drawing_spec=drawing_spec)
                # connection_drawing_spec=mp_drawing_styles     <---- 이 부분, 눈썹과 눈, 오른쪽 왼쪽 색깔(초록색, 빨강색)
                # .get_default_face_mesh_contours_style())

        
        whole_area = 0
        # 얼굴 전체의 크기 측정, 얼굴을 한 점을 공유하는 여러 개의 삼각형으로 나누어 삼각형의 넓이를 더함으로써 얼굴 넓이 측정
        for i, idx in enumerate(oval) :
                if idx == 109 :
                        x_gap = face_landmarks.landmark[oval[i]].x - face_landmarks.landmark[oval[0]].x
                        y_gap = face_landmarks.landmark[oval[i]].y - face_landmarks.landmark[oval[0]].y
                        A = np.array([[y_gap/x_gap, -1], [-x_gap/y_gap, -1]])
                        B = np.array([y_gap/x_gap*face_landmarks.landmark[oval[i]].x-face_landmarks.landmark[oval[i]].y, -x_gap/y_gap*face_landmarks.landmark[5].x-face_landmarks.landmark[5].y])
                        x,y = np.linalg.solve(A,B)
                else :
                        x_gap = face_landmarks.landmark[oval[i]].x - face_landmarks.landmark[oval[i+1]].x
                        y_gap = face_landmarks.landmark[oval[i]].y - face_landmarks.landmark[oval[i+1]].y
                        A = np.array([[y_gap/x_gap, -1], [-x_gap/y_gap, -1]])
                        B = np.array([y_gap/x_gap*face_landmarks.landmark[oval[i]].x-face_landmarks.landmark[oval[i]].y, -x_gap/y_gap*face_landmarks.landmark[5].x-face_landmarks.landmark[5].y])
                        x,y = np.linalg.solve(A,B)
                vertical_x = face_landmarks.landmark[5].x - x
                vertical_y = face_landmarks.landmark[5].y - y
                temp = (np.sqrt(x_gap**2 + y_gap**2) * np.sqrt(vertical_x**2 + vertical_y**2)) / 2
                whole_area = whole_area + temp

        # 눈 양 끝, 아랫입술 가운데의 landmark를 이용해서 삼각형을 그리고 이목구비를 구분해준다.
        # 이목구비/전체얼굴 비율을 구한다. 
        eye_x = face_landmarks.landmark[226].x - face_landmarks.landmark[446].x
        eye_y = face_landmarks.landmark[226].y - face_landmarks.landmark[446].y
        A = np.array([[eye_y/eye_x, -1], [-eye_x/eye_y, -1]])
        B = np.array([eye_y/eye_x*face_landmarks.landmark[226].x-face_landmarks.landmark[226].y, -eye_x/eye_y*face_landmarks.landmark[17].x-face_landmarks.landmark[17].y])
        x,y = np.linalg.solve(A,B)
        vertical_x = face_landmarks.landmark[17].x - x
        vertical_y = face_landmarks.landmark[17].y - y
        face_area = (np.sqrt(eye_x**2 + eye_y**2) * np.sqrt(vertical_x**2 + vertical_y**2)) / 2

        face_ratio = whole_area/face_area
        print("face ratio : ", face_ratio)

        # 결과값이 4.6 이상이면 여백이 많은 얼굴
        if (face_ratio > 4.6) :
            is_wide_margin = True
        else :
            is_wide_margin = False
        print("is_wide_margin = ",is_wide_margin)


        # 눈 양 끝, 아랫입술 가운데의 landmark를 이용해서 삼각형을 그리고 이목구비/전체얼굴 비율을 구한다. 
        eye_x = face_landmarks.landmark[33].x - face_landmarks.landmark[263].x
        eye_y = face_landmarks.landmark[33].y - face_landmarks.landmark[263].y
        
        ## 얼굴 비율 측정 1, 긴 중안부 판단
        # 두 눈의 길이와 눈-코 길이 비교
        A = np.array([[eye_y/eye_x, -1], [-eye_x/eye_y, -1]])
        B = np.array([eye_y/eye_x*face_landmarks.landmark[33].x-face_landmarks.landmark[33].y, -eye_x/eye_y*face_landmarks.landmark[94].x-face_landmarks.landmark[94].y])
        x,y = np.linalg.solve(A,B)
        EtN_vertical_x = face_landmarks.landmark[94].x - x
        EtN_vertical_y = face_landmarks.landmark[94].y - y

        # Eye to Nose length
        EtN_len = np.sqrt(EtN_vertical_x**2 + EtN_vertical_y**2)  
        Eyes_len = np.sqrt(eye_x**2 + eye_y**2)
        
        # 결과값이 4.7 이상이면 긴 중안부
        if ((EtN_len/Eyes_len*10) > 4.7) :
            is_long_mid = True
        else :
            is_long_mid = False
        print("is_long_mid = ",is_long_mid)

        ## 얼굴 비율 측정 3, 긴 턱 판단 (중안부와 하안부의 비율)
        eyebrow_x = face_landmarks.landmark[105].x - face_landmarks.landmark[334].x
        eyebrow_y = face_landmarks.landmark[105].y - face_landmarks.landmark[334].y
        
        # 중안부 길이 구하기(눈썹 중간 - 코 끝)
        A = np.array([[eyebrow_y/eyebrow_x, -1], [-eyebrow_x/eyebrow_y, -1]])
        B = np.array([eyebrow_y/eyebrow_x*face_landmarks.landmark[105].x-face_landmarks.landmark[105].y, -eyebrow_x/eyebrow_y*face_landmarks.landmark[94].x-face_landmarks.landmark[94].y])
        x,y = np.linalg.solve(A,B)
        middle_face_x = face_landmarks.landmark[94].x - x
        middle_face_y = face_landmarks.landmark[94].y - y

        # Brow to Nose length
        BtN_len = np.sqrt(middle_face_x**2 + middle_face_y**2)
        
        # 하안부 길이 구하는 방법, 중안부의 길이를 빼줌
        A = np.array([[eyebrow_y/eyebrow_x, -1], [-eyebrow_x/eyebrow_y, -1]])
        B = np.array([eyebrow_y/eyebrow_x*face_landmarks.landmark[105].x-face_landmarks.landmark[105].y, -eyebrow_x/eyebrow_y*face_landmarks.landmark[152].x-face_landmarks.landmark[152].y])
        x,y = np.linalg.solve(A,B)
        middle_lower_face_x = face_landmarks.landmark[152].x - x
        middle_lower_face_y = face_landmarks.landmark[152].y - y

        # Eyebrow to Chin length
        BtC_len = np.sqrt(middle_lower_face_x**2 + middle_lower_face_y**2)

        middle_lower_length_ratio = BtN_len/(BtC_len-BtN_len)

        # 결과값이 1.1보다 작으면, 긴 턱
        if middle_lower_length_ratio < 1.1 :
            is_long_chin = True

        ## 얼굴 비율 측정 3, 긴 턱 판단 (인중 길이 대비 턱의 길이가 2배보다 길때)  
        else :
            # 코끝 - 윗 입술
            injung_x = face_landmarks.landmark[94].x - face_landmarks.landmark[0].x
            injung_y = face_landmarks.landmark[94].y - face_landmarks.landmark[0].y

            InJung_len = np.sqrt(injung_x**2 + injung_y**2)
          
            # 아랫 입술 - 턱 끝
            chin_x = face_landmarks.landmark[17].x - face_landmarks.landmark[152].x
            chin_y = face_landmarks.landmark[17].y - face_landmarks.landmark[152].y

            Chin_len = np.sqrt(chin_x**2 + chin_y**2)

            # 결과값이 1보다 크면, 긴 턱
            if Chin_len/(2*InJung_len) > 1:
                is_long_chin = True
            else :
                is_long_chin = False
        print("is_long_chin : ",is_long_chin)

        ## 얼굴 비율 측정 2, 하안부 중 긴 인중 판단
        nose2lip_x = face_landmarks.landmark[94].x - face_landmarks.landmark[17].x
        nose2lip_y = face_landmarks.landmark[94].y - face_landmarks.landmark[17].y
        lip2chin_x = face_landmarks.landmark[17].x - face_landmarks.landmark[152].x
        lip2chin_y = face_landmarks.landmark[17].y - face_landmarks.landmark[152].y
        
        # Nose to Under-Lip length
        NtL_len = np.sqrt(nose2lip_x**2 + nose2lip_y**2)

        # Under-Lip to Chin length
        LtC_len = np.sqrt(lip2chin_x**2 + lip2chin_y**2)

        length_ratio = (NtL_len*0.8)/LtC_len

        # 결과값이 0.9 이상이면 긴 중안부
        if length_ratio > 0.9:
            is_long_philtrum = True
        else :
            is_long_philtrum = False
        print("is_long_philtrum = ",is_long_philtrum)


        cv2.imshow("Image_ESEntial",annotated_image)
       
        # esc 입력시 종료
        key = cv2.waitKey(50000)
        if key == 27:
            break