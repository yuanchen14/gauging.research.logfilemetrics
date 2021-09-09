from enum import Enum


class EventType(Enum):
    AddPoint = 0
    AddPoints = 1
    DeletePoints = 2
    DeletePoint = 3
    ChangeAttributeProfile = 4
    ChangeObjectTypeProfile = 5
    ChangeOffsetProfile = 6
    ChangePointCodePoint = 7
    ChangePointCodePoints = 8
    MovePointPoint = 9
    MovePointPoints = 10
    ConnectLinesPoints = 11
    InterpolatePointsProfile = 12
    InterpolatePointsPoints = 13
    MergeLinesPoints = 14
    SwapTwoPoints = 15
    PastePoints = 16
    DrapePoints = 17
    PasteDrapePoints = 18
    # UNDO Actions
    UndoAddPoint = 19
    UndoAddPoints = 20
    UndoDeletePoints = 21
    UndoDeletePoint = 22
    UndoChangeAttributeProfile = 23
    UndoChangeObjectTypeProfile = 24
    UndoChangeOffsetProfile = 25
    UndoChangePointCodePoint = 26
    UndoChangePointCodePoints = 27
    UndoMovePointPoint = 28
    UndoMovePointPoints = 29
    UndoConnectLinesPoints = 30
    UndoInterpolatePointsProfile = 31
    UndoInterpolatePointsPoints = 32
    UndoMergeLinesPoints = 33
    UndoSwapTwoPoints = 34
    UndoPastePoints = 35
    UndoDrapePoints = 36
    UndoPasteDrapePoints = 37



