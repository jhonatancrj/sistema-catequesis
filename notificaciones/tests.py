from django.test import TestCase
from django.contrib.auth.models import User
from .models import Notificacion, PreferenciaNotificacion, TipoNotificacion, CanalNotificacion
from .services import NotificacionService


class NotificacionServiceTestCase(TestCase):
    def setUp(self):
        """Crear datos de prueba"""
        self.usuario1 = User.objects.create_user(
            username='usuario1',
            email='usuario1@test.com',
            password='testpass123'
        )
        self.usuario2 = User.objects.create_user(
            username='usuario2',
            email='usuario2@test.com',
            password='testpass123'
        )

    def test_crear_notificacion_simple(self):
        """Test crear notificación simple"""
        notificaciones = NotificacionService.crear_notificacion(
            usuarios=self.usuario1,
            tipo=TipoNotificacion.CURSO_CREADO,
            titulo='Test Curso',
            mensaje='Mensaje de prueba',
            canales=[CanalNotificacion.EN_APP]
        )

        self.assertEqual(len(notificaciones), 1)
        self.assertEqual(notificaciones[0].titulo, 'Test Curso')
        self.assertEqual(notificaciones[0].usuario, self.usuario1)

    def test_crear_notificacion_multiple(self):
        """Test crear notificación para múltiples usuarios"""
        notificaciones = NotificacionService.crear_notificacion(
            usuarios=[self.usuario1, self.usuario2],
            tipo=TipoNotificacion.CALIFICACION_CAMBIO,
            titulo='Test Múltiple',
            mensaje='Mensaje para múltiples',
            canales=[CanalNotificacion.EN_APP]
        )

        self.assertEqual(len(notificaciones), 2)

    def test_marcar_como_leida(self):
        """Test marcar notificación como leída"""
        notif = Notificacion.objects.create(
            usuario=self.usuario1,
            tipo=TipoNotificacion.CURSO_CREADO,
            canal=CanalNotificacion.EN_APP,
            titulo='Test',
            mensaje='Test'
        )

        self.assertFalse(notif.leida)
        notif.marcar_como_leida()
        notif.refresh_from_db()
        self.assertTrue(notif.leida)
        self.assertIsNotNone(notif.fecha_lectura)

    def test_obtener_count_no_leidas(self):
        """Test contar notificaciones no leídas"""
        # Crear 3 notificaciones no leídas
        for i in range(3):
            Notificacion.objects.create(
                usuario=self.usuario1,
                tipo=TipoNotificacion.CURSO_CREADO,
                canal=CanalNotificacion.EN_APP,
                titulo=f'Test {i}',
                mensaje='Test'
            )

        count = NotificacionService.obtener_count_no_leidas(self.usuario1)
        self.assertEqual(count, 3)

    def test_preferencias_notificacion(self):
        """Test preferencias de notificación"""
        pref = PreferenciaNotificacion.objects.create(usuario=self.usuario1)

        self.assertTrue(pref.cursos_nuevos)
        self.assertTrue(pref.email_habilitado)
        self.assertFalse(pref.whatsapp_habilitado)

    def test_verificar_preferencias(self):
        """Test verificación de preferencias"""
        pref = PreferenciaNotificacion.objects.create(
            usuario=self.usuario1,
            cursos_nuevos=True,
            calificaciones_cambios=False
        )

        # Debe permitir notificaciones de cursos
        self.assertTrue(NotificacionService._verificar_preferencias(
            TipoNotificacion.CURSO_CREADO, pref
        ))

        # No debe permitir notificaciones de calificaciones
        self.assertFalse(NotificacionService._verificar_preferencias(
            TipoNotificacion.CALIFICACION_CAMBIO, pref
        ))
