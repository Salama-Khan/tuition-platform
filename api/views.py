from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from subjects.models import Subject, UserSubject

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    return Response({"id": request.user.id, "username": request.user.username})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def subjects(request):
    data = [{"id": s.id, "code": s.code, "name": s.name} for s in Subject.objects.all().order_by('name')]
    return Response(data)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def my_subjects(request):
    if request.method == 'POST':
        ids = request.data.get('subject_ids', [])
        UserSubject.objects.filter(user=request.user).delete()
        for sid in ids:
            UserSubject.objects.create(user=request.user, subject_id=sid)
    mine = [{"id": us.subject.id, "code": us.subject.code, "name": us.subject.name}
            for us in UserSubject.objects.filter(user=request.user).select_related('subject')]
    return Response(mine)
