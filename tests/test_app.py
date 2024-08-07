import unittest
from app import app, db, Usuarios, Temas, Respuestas

class TestApp(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_registro_usuario(self):
        response = self.app.post('/registro', data=dict(
            username='testuser',
            email='test@example.com',
            password='password123'
        ), follow_redirects=True)
        self.assertIn(b'¡Registro exitoso!', response.data)

    def test_login_usuario(self):
        usuario = Usuarios(nombre_usuario='testuser', email='test@example.com', contraseña='password123')
        db.session.add(usuario)
        db.session.commit()

        response = self.app.post('/login', data=dict(
            username='testuser',
            password='password123'
        ), follow_redirects=True)
        self.assertIn(b'¡Inicio de sesión exitoso!', response.data)

    def test_agregar_tema(self):
        usuario = Usuarios(nombre_usuario='testuser', email='test@example.com', contraseña='password123')
        db.session.add(usuario)
        db.session.commit()
        with self.app:
            self.app.post('/login', data=dict(
                username='testuser',
                password='password123'
            ), follow_redirects=True)
            response = self.app.post('/agregar_tema', data=dict(
                titulo='Test Tema',
                descripcion='Descripción del tema de prueba'
            ), follow_redirects=True)
            self.assertIn(b'Descripción del tema de prueba', response.data)

    def test_agregar_respuesta(self):
        usuario = Usuarios(nombre_usuario='testuser', email='test@example.com', contraseña='password123')
        db.session.add(usuario)
        db.session.commit()
        tema = Temas(titulo='Test Tema', descripcion='Descripción del tema de prueba', id_usuario=usuario.id, fecha_creacion=datetime.now())
        db.session.add(tema)
        db.session.commit()
        with self.app:
            self.app.post('/login', data=dict(
                username='testuser',
                password='password123'
            ), follow_redirects=True)
            response = self.app.post(f'/temas/{tema.id}/agregar_respuesta', data=dict(
                contenido='Respuesta de prueba',
                calificacion=5
            ), follow_redirects=True)
            self.assertIn(b'Respuesta y calificación agregadas satisfactoriamente', response.data)

if __name__ == '__main__':
    unittest.main()
