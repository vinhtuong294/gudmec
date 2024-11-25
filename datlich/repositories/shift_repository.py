from ..models import Shift

class ShiftRepository:
    @staticmethod
    def find_all():
        """
        Lấy tất cả các Shift.
        """
        return Shift.objects.all()

    @staticmethod
    def find_by_id(shift_id):
        """
        Tìm Shift theo ID.
        """
        return Shift.objects.filter(id=shift_id).first()
