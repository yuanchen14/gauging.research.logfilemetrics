from enum import Enum


class EventType(Enum):
    AddPoint = "add point"
    DeletePoint = "delete point"
    ChangeAttributeProfile = "change attribute"
    ChangeObjectTypeProfile = "change object"
    ChangeOffsetProfile = "change offset"
    ChangePointCodePoint = "change point code"
    MovePoint = "move point"
    ConnectLinesPoint = "connect lines"
    InterpolatePointsProfile = "interpolate all points"
    InterpolatePointsPoint = "interpolate points"
    MergeLinesPoint = "merge lines"
    SwapTwoPoint = "swap points"
    PastePoint = "paste points"
    DrapePoint = "drape points"
    PasteDrapePoint = "paste and drape points"
    CloseProfile = "close profile"
    OpenProfile = "open profile"
    # UNDO Actions
    UndoAddPoint = 17
    UndoDeletePoint = 18
    UndoChangeAttributeProfile = 19
    UndoChangeObjectTypeProfile = 20
    UndoChangeOffsetProfile = 21
    UndoChangePointCodePoint = 22
    UndoMovePoint = 23
    UndoConnectLinesPoint = 24
    UndoInterpolatePointsProfile = 25
    UndoInterpolatePointsPoint = 26
    UndoMergeLinesPoint = 27
    UndoSwapTwoPoint = 28
    UndoPastePoint = 29
    UndoDrapePoint = 30
    UndoPasteDrapePoint = 31



