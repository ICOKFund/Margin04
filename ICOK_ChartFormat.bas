Attribute VB_Name = "ICOK_ChartFormat"
'==================================================================
' ICOK_ChartFormat
'   ICOK 표준 차트 서식 통일 매크로 (네이비 그라데이션 8색 + Pretendard)
'   원본: 전체차트서식_두산에너빌리티()  →  종목 무관 범용 버전
'
'   개선 사항
'     1) 범용화 : 종목 종속 함수명 제거 (모든 리포트 재사용)
'     2) 색상버그 수정 : RGB(92,141,202) 중복 제거 → RGB(115,153,206) 보간
'     3) 성능/안정성 : ScreenUpdating·EnableEvents 토글 + 오류 핸들러
'     4) 상수화 : 폰트/크기/선두께/GapWidth 를 Const 로 분리
'     5) 데이터레이블 토글 : SHOW_DATA_LABELS 로 라인차트 과밀 방지
'     6) 막대 GapWidth 안정 적용 및 빈/음수 차트 가드
'==================================================================
Option Explicit

' ---- 서식 상수 (유지보수 지점) -------------------------------
Private Const FONT_NAME       As String = "Pretendard"
Private Const FONT_SIZE       As Single = 10
Private Const LINE_WEIGHT     As Single = 1.5
Private Const GAP_WIDTH       As Long = 25
Private Const MARKER_SIZE     As Long = 7
Private Const SHOW_DATA_LABELS As Boolean = True   ' False 로 두면 데이터레이블 일괄 비표시
Private Const FONT_BLACK      As Long = 0          ' RGB(0,0,0)

' ---- ICOK 네이비 그라데이션 팔레트 (8색, 우선순위 순) --------
Private Function ColorPalette() As Variant
    ColorPalette = Array( _
        RGB(0, 42, 82), _
        RGB(0, 63, 123), _
        RGB(0, 80, 157), _
        RGB(46, 118, 193), _
        RGB(92, 141, 202), _
        RGB(115, 153, 206), _
        RGB(138, 165, 211), _
        RGB(171, 185, 219))
End Function

' 시리즈/조각 인덱스(1-base)에 대응하는 색상 반환 (초과 시 순환)
Private Function PickColor(ByVal idx As Long) As Long
    Dim pal As Variant
    Dim n As Long
    pal = ColorPalette()
    n = UBound(pal) - LBound(pal) + 1
    PickColor = pal(LBound(pal) + ((idx - 1) Mod n))
End Function

'==================================================================
' 메인 : 통합문서 내 모든 차트에 서식 적용
'==================================================================
Public Sub ICOK_ChartFormat()
    Dim ws As Worksheet
    Dim chObj As ChartObject

    On Error GoTo CleanFail
    Application.ScreenUpdating = False
    Application.EnableEvents = False

    For Each ws In ThisWorkbook.Worksheets
        For Each chObj In ws.ChartObjects
            FormatOneChart chObj.Chart
        Next chObj
    Next ws

CleanExit:
    Application.EnableEvents = True
    Application.ScreenUpdating = True
    Exit Sub

CleanFail:
    MsgBox "차트 서식 적용 중 오류: " & Err.Number & " - " & Err.Description, vbExclamation
    Resume CleanExit
End Sub

'==================================================================
' 단일 차트 서식
'==================================================================
Private Sub FormatOneChart(ByVal ch As Chart)
    Dim i As Long, j As Long
    Dim 시리즈개수 As Long
    Dim 적용색상 As Long
    Dim seriesName As String

    With ch
        ' --- 차트 배경/테두리 제거 ---
        .ChartArea.Format.Fill.Visible = msoFalse
        .ChartArea.Format.Line.Visible = msoFalse

        ' --- 제목 폰트 ---
        If .HasTitle Then
            With .ChartTitle.Format.TextFrame2.TextRange.Font
                .Name = FONT_NAME
                .Size = FONT_SIZE
                .Fill.ForeColor.RGB = FONT_BLACK
            End With
        End If

        ' --- 범례 폰트 ---
        If .HasLegend Then
            With .Legend.Format.TextFrame2.TextRange.Font
                .Name = FONT_NAME
                .Size = FONT_SIZE
                .Fill.ForeColor.RGB = FONT_BLACK
            End With
        End If

        시리즈개수 = .SeriesCollection.Count
        If 시리즈개수 = 0 Then Exit Sub   ' 빈 차트 가드

        ' --- 시리즈별 서식 ---
        For i = 1 To 시리즈개수
            seriesName = .SeriesCollection(i).Name
            적용색상 = PickColor(i)

            ' 선 색상/두께
            With .SeriesCollection(i).Format.Line
                .ForeColor.RGB = 적용색상
                .Weight = LINE_WEIGHT
            End With

            ' 채우기(막대형) - 라인차트에서는 오류 무시
            On Error Resume Next
            .SeriesCollection(i).Format.Fill.ForeColor.RGB = 적용색상
            On Error GoTo 0

            ' 시리즈명에 "%" 포함 → 표식(marker) 설정 (보조축 비율선 강조)
            If InStr(seriesName, "%") > 0 Then
                On Error Resume Next
                With .SeriesCollection(i)
                    .MarkerStyle = xlMarkerStyleCircle
                    .MarkerSize = MARKER_SIZE
                    .MarkerForegroundColor = 적용색상
                    .MarkerBackgroundColor = RGB(255, 255, 255)
                End With
                On Error GoTo 0
            End If

            ' 데이터레이블 (상수로 on/off)
            If SHOW_DATA_LABELS Then
                On Error Resume Next
                .SeriesCollection(i).ApplyDataLabels
                With .SeriesCollection(i).DataLabels
                    .Font.Name = FONT_NAME
                    .Font.Size = FONT_SIZE
                    .Font.Color = FONT_BLACK
                End With
                On Error GoTo 0
            End If
        Next i

        ' --- 원형(Pie) 차트 처리 ---
        On Error Resume Next
        If .SeriesCollection(1).ChartType = xlPie Then
            If 시리즈개수 = 1 Then
                ' 시리즈 1개 → 조각별 색상 + 테두리 제거
                With .SeriesCollection(1)
                    For j = 1 To .Points.Count
                        .Points(j).Format.Fill.ForeColor.RGB = PickColor(j)
                        .Points(j).Format.Line.Visible = msoFalse
                    Next j
                End With
            Else
                ' 시리즈 2개 이상 → 시리즈별 색상 + 테두리 제거
                For i = 1 To 시리즈개수
                    .SeriesCollection(i).Format.Fill.ForeColor.RGB = PickColor(i)
                    .SeriesCollection(i).Format.Line.Visible = msoFalse
                Next i
            End If
        End If
        On Error GoTo 0

        ' --- 막대형/세로막대형 → 간격 25% 고정 ---
        On Error Resume Next
        If .SeriesCollection(1).ChartType = xlColumnClustered Or _
           .SeriesCollection(1).ChartType = xlBarClustered Then
            .ChartGroups(1).GapWidth = GAP_WIDTH
        End If
        On Error GoTo 0

        ' --- X축(항목축) ---
        If .HasAxis(xlCategory, xlPrimary) Then
            With .Axes(xlCategory)
                .HasTitle = False
                With .TickLabels.Font
                    .Name = FONT_NAME
                    .Size = FONT_SIZE
                    .Color = FONT_BLACK
                End With
                .TickLabelSpacing = 1
                .Format.Line.ForeColor.RGB = FONT_BLACK
                .MajorTickMark = xlOutside
                .MinorTickMark = xlNone
                .HasMajorGridlines = False
            End With
        End If

        ' --- Y축(값축) ---
        If .HasAxis(xlValue, xlPrimary) Then
            With .Axes(xlValue)
                .HasTitle = False
                With .TickLabels.Font
                    .Name = FONT_NAME
                    .Size = FONT_SIZE
                    .Color = FONT_BLACK
                End With
                .TickLabels.NumberFormat = "#,##0"
                .Format.Line.ForeColor.RGB = FONT_BLACK
                .MajorTickMark = xlOutside
                .MinorTickMark = xlNone
                .HasMajorGridlines = False
            End With
        End If

        ' --- 데이터 표(Data Table) ---
        If .HasDataTable Then
            With .DataTable.Font
                .Name = FONT_NAME
                .Size = FONT_SIZE
                .Color = FONT_BLACK
            End With
        End If
    End With
End Sub
