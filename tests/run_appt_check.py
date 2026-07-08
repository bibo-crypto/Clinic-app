from controllers import appointment_controller
appts = appointment_controller.get_all()
print('count', len(appts))
for a in appts[:5]:
    print('appt', a.id, a.date, str(a.time)[:5], 'patient=', getattr(a.patient, 'full_name', None), 'doctor=', getattr(a.doctor, 'full_name', None))
