# -*-coding:utf8;-*-
'''
이미지에서 테이블(그리드) 구조 추출하는 함수

김남길 (2017.12.26) : 초본 생성

'''


def get_intersection_point(hp1, hp2, vp1, vp2):
    '''
    두 직선의 교차점을 구하는 함수
    여기서는 세로줄과 가로줄의 교차점을 구하여 그리드 셀(rectangle)을 구할 때 사용한다.
    참고 http://www.gisdeveloper.co.kr/?p=89
    :param hp1: First point of the horizontal line segment.
    :param hp2: Second point of the horizontal line segment.
    :param vp1: First point of the vertical line segment.
    :param vp2: Second point of the vertical line segment.
    :return: intersection point if not exists then None
    '''

    under = (vp2[1] - vp1[1]) * (hp2[0] - hp1[0]) - (vp2[0] - vp1[0]) * (hp2[1] - hp1[1])
    if under == 0:
        return None

    _t = (vp2[0] - vp1[0]) * (hp1[1] - vp1[1]) - (vp2[1] - vp1[1]) * (hp1[0] - vp1[0])
    _s = (hp2[0] - hp1[0]) * (hp1[1] - vp1[1]) - (hp2[1] - hp1[1]) * (hp1[0] - vp1[0])

    t = _t / under
    s = _s / under

    if t < 0.0 or t > 1.0 or s < 0.0 or s > 1.0:
        return None
    if (_t == 0 and _s == 0):
        return None

    x = hp1[0] + t * (hp2[0] - hp1[0])
    y = hp1[1] + t * (hp2[1] - hp1[1])

    return (int(x), int(y))


def get_grid_cell(horizontal_line, vertical_line):
    '''
    가로선을 기준으로 좌상단교차점, 우상단교차점, 좌하단교차점, 우하단교차점을 찾았을 때 모두 존재하면 table에서 cell로 인정한다.
    :param horizontal_line: tuples of vertical line start end points
    :param vertical_line: tuples of horizontal line start end points
    :return: cell point (rectangle -> 좌상단, 우하단) list
    '''

    # 세로줄은 X좌표 기준으로 가로줄은 Y좌표 기준으로 정렬
    vertical_lines_sorted = sorted(vertical_line, key=lambda vertical: vertical[0])
    horizontal_lines_sorted = sorted(horizontal_line, key=lambda horizontal: horizontal[1])    
    grid_cells = []
    # 기준 가로선 루핑 시작
    for i in range(len(horizontal_lines_sorted)):
        # 기준 세로 루핑 시작
        for j in range(len(vertical_lines_sorted)):
            hp1 = (horizontal_lines_sorted[i][0], horizontal_lines_sorted[i][1])
            hp2 = (horizontal_lines_sorted[i][2], horizontal_lines_sorted[i][3])
            vp1 = (vertical_lines_sorted[j][0], vertical_lines_sorted[j][1])
            vp2 = (vertical_lines_sorted[j][2], vertical_lines_sorted[j][3])
            # 기준이 되는 가로선과 세로선의 교차점을 찾는다.
            left_top = get_intersection_point(hp1, hp2, vp1, vp2)
            # 교차점이 없거나 기준세로선이 마지막 선이면 더 이상 진행하지 않음.
            if (left_top != None and j + 1 < len(vertical_lines_sorted)):
                is_find_cell = False
                # 기준가로줄에 걸쳐있는 세로줄 검색
                for k in range(len(vertical_lines_sorted)):
                    # 기준 세로선 보다 우측에 있는 세로선 중에 교차점을 갖고 있는 첫번 째 세로선을 검색
                    if j < k:
                        hp1 = (horizontal_lines_sorted[i][0], horizontal_lines_sorted[i][1])
                        hp2 = (horizontal_lines_sorted[i][2], horizontal_lines_sorted[i][3])
                        vp1 = (vertical_lines_sorted[k][0], vertical_lines_sorted[k][1])
                        vp2 = (vertical_lines_sorted[k][2], vertical_lines_sorted[k][3])
                        right_top = get_intersection_point(hp1, hp2, vp1, vp2)
                        if (right_top != None and i + 1 < len(horizontal_lines_sorted)):
                            # 기준가로줄선에 걸쳐있는 기준세로선과 둘다 걸쳐 있는 다음가로선 검색
                            for l in range(len(horizontal_lines_sorted)):
                                if i < l:
                                    hp1 = (horizontal_lines_sorted[l][0], horizontal_lines_sorted[l][1])
                                    hp2 = (horizontal_lines_sorted[l][2], horizontal_lines_sorted[l][3])
                                    vp1 = (vertical_lines_sorted[j][0], vertical_lines_sorted[j][1])
                                    vp2 = (vertical_lines_sorted[j][2], vertical_lines_sorted[j][3])
                                    left_bottom = get_intersection_point(hp1, hp2, vp1, vp2)                                    
                                    if (left_bottom != None):
                                        # 다음가로선과 다음세로선의 교차점 검
                                        hp1 = (horizontal_lines_sorted[l][0], horizontal_lines_sorted[l][1])
                                        hp2 = (horizontal_lines_sorted[l][2], horizontal_lines_sorted[l][3])
                                        vp1 = (vertical_lines_sorted[k][0], vertical_lines_sorted[k][1])
                                        vp2 = (vertical_lines_sorted[k][2], vertical_lines_sorted[k][3])
                                        right_bottom = get_intersection_point(hp1, hp2, vp1, vp2)
                                        # 우하단 교차점까지 찾은면 리스트에 좌상단, 우하단 교차점의 좌표을 추가한다.
                                        if (right_bottom != None):                                            
                                            grid_cells.append(left_top + right_bottom)
                                            is_find_cell = True
                                            break
                    # 중복으로 그리드 셀 찾기를 방지하기 위한 break
                    if is_find_cell:
                        break

    return grid_cells


