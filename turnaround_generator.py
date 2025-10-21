import maya.cmds as cmds
import maya.mel as mel
import sys
import playblast_generator
import maya.cmds as cmds
import playblast_generator

class TurnAroundPlayblastGenerator(playblast_generator.PlayblastGenerator):
    """
    playblast generator 클래스를 상속받아
    카메라를 생성하고, 턴어라운드 플레이블라스트를 생성하는 클래스
    """
    def __init__(self):
        super().__init__()
        self.__turnaround_cam = "publish_turnaround_cam"  # 턴어라운드 카메라 이름
        self.__turnaround_cam_group = "publish_turnaround_cam_group"  # 턴어라운드 카메라 그룹 이름
        self.user_camera_name = ""  # 유저가 사용하고 있는 기존 persp 뷰의 카메라 이름
        self.__offset_pos = {
            "translateX": 0,
            "translateY": 12,
            "translateZ": 70,
            "rotateX": 0,
            "rotateY": 0,
            "rotateZ": 0
        }
        # 기본 프레임레인지: 1 ~ 120
        self.set_frame_range(1, 120)
        self._path = ""

    def get_offset_pos(self):
        return self.__offset_pos

    def set_offset_pos(self, tx=None, ty=None, tz=None, rx=None, ry=None, rz=None):
        """
        턴어라운드 카메라의 초기 위치를 설정하는 메서드
        """
        self.__offset_pos["translateX"] = tx if tx is not None else self.__offset_pos["translateX"]
        self.__offset_pos["translateY"] = ty if ty is not None else self.__offset_pos["translateY"]
        self.__offset_pos["translateZ"] = tz if tz is not None else self.__offset_pos["translateZ"]
        self.__offset_pos["rotateX"] = rx if rx is not None else self.__offset_pos["rotateX"]
        self.__offset_pos["rotateY"] = ry if ry is not None else self.__offset_pos["rotateY"]
        self.__offset_pos["rotateZ"] = rz if rz is not None else self.__offset_pos["rotateZ"]

    def create_turnaround_camera(self):
        """
        턴어라운드 카메라를 생성하는 메서드
        """
        if cmds.objExists(self.__turnaround_cam):
            cmds.delete(self.__turnaround_cam)
        if cmds.objExists(self.__turnaround_cam_group):
            cmds.delete(self.__turnaround_cam_group)

        # 카메라 생성
        self.__turnaround_cam = cmds.camera()[0]
        self.__turnaround_cam = cmds.rename(self.__turnaround_cam, "publish_turnaround_cam")

        # 카메라 위치 설정
        for key, value in self.__offset_pos.items():
            cmds.setAttr(f"{self.__turnaround_cam}.{key}", value)

        # 카메라 오프셋 그룹 생성
        cmds.select(clear=True)
        self.__turnaround_cam_group = cmds.group(name="publish_turnaround_cam_group", empty=True)
        cmds.parent(self.__turnaround_cam, self.__turnaround_cam_group)

        # 카메라 그룹에 애니메이션 설정
        cmds.setKeyframe(self.__turnaround_cam_group, attribute="rotateY", value=0, time=1)
        cmds.setKeyframe(self.__turnaround_cam_group, attribute="rotateY", value=360, time=120)
        cmds.selectKey(self.__turnaround_cam_group, time=(1, 120), attribute="rotateY")
        cmds.keyTangent(inTangentType="linear", outTangentType="linear")

    def delete_camera(self):
        """
        만든 턴어라운드 카메라를 삭제하는 메서드
        """
        if cmds.objExists(self.__turnaround_cam):
            cmds.delete(self.__turnaround_cam)
        if cmds.objExists(self.__turnaround_cam_group):
            cmds.delete(self.__turnaround_cam_group)

    def get_persp_camera(self):
        """
        현재 persp 뷰에서 사용 중인 카메라 이름을 반환
        """
        panel = cmds.getPanel(withFocus=True)
        if cmds.getPanel(typeOf=panel) == "modelPanel":
            return cmds.modelPanel(panel, query=True, camera=True)
        return "persp"

    def set_persp_camera(self, camera_name):
        """
        현재 활성화된 persp 뷰에 카메라를 설정
        """
        for panel in cmds.getPanel(allPanels=True):
            if cmds.getPanel(typeOf=panel) == "modelPanel":
                cmds.modelPanel(panel, edit=True, camera=camera_name)

    def create_turnaround_playblast(self, path=None, start_frame=None, end_frame=None):
        """
        턴어라운드 카메라 playblast 생성하는 메서드
        """
        if path:
            self.set_path(path)

        # 프레임 범위 설정
        if start_frame is not None:
            self._playblast_options['startTime'] = start_frame
        if end_frame is not None:
            self._playblast_options['endTime'] = end_frame

        # 기존 persp 뷰 카메라 저장
        self.user_camera_name = self.get_persp_camera()

        # 턴어라운드 카메라 생성 및 설정
        self.create_turnaround_camera()
        self.set_persp_camera(self.__turnaround_cam)

        return self.run()

    def run(self):
        """
        플레이블라스트 실행
        """
        first_frame = self._playblast_options['startTime']
        last_frame = self._playblast_options['endTime'] - 1

        if not self.get_path():
            raise ValueError("Playblast 경로가 설정되지 않았습니다.")

        self.playblast(self._path, first_frame, last_frame)

        # 원래 persp 카메라로 복원
        self.set_persp_camera(self.user_camera_name)

        # 턴어라운드 카메라 삭제
        self.delete_camera()

        return self._path


if __name__ == "__main__":
    import sys
    import importlib

    sys.path.append('/home/rapa/NA_Spirit/maya/turnaround')

    import turnaround_playblast_generator
    importlib.reload(turnaround_playblast_generator)

    tap = TurnAroundPlayblastGenerator()

    path = "/home/rapa/비디오/test.mov"
    tap.create_turnaround_playblast(path=path)