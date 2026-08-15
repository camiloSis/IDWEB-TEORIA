/* ============================================
   PROYECTO FINAL - DESARROLLO WEB
   Archivo: script.js
   Funcionalidades JavaScript requeridas:
   1. Sistema de navegación entre pestañas
   2. Validación de formulario de contacto
   ============================================ */

// ============================================
// FUNCIONALIDAD 1: NAVEGACIÓN ENTRE PESTAÑAS
// ============================================

/**
 * Función principal para cambiar entre pestañas/secciones
 * Esta función se ejecuta cuando el usuario hace clic en un botón de navegación
 * 
 * @param {string} tabId - El ID de la sección que queremos mostrar
 * 
 * Proceso:
 * 1. Oculta todas las secciones
 * 2. Desactiva todos los botones
 * 3. Muestra solo la sección seleccionada
 * 4. Activa el botón correspondiente
 */
function showTab(tabId, event) {
    // PASO 1: Ocultar todas las secciones
    // Seleccionamos todos los elementos que tengan la clase 'contenidoSeccion'
    const todasLasSecciones = document.querySelectorAll('.contenidoSeccion');
    
    // Recorremos cada sección y le removemos la clase 'active'
    todasLasSecciones.forEach(function(seccion) {
        seccion.classList.remove('active');
    });

    // PASO 2: Desactivar todos los botones de navegación
    // Seleccionamos todos los botones con la clase 'botondePestaña'
    const todosLosBotones = document.querySelectorAll('.botondePestaña');
    
    // Recorremos cada botón y le removemos la clase 'active'
    todosLosBotones.forEach(function(boton) {
        boton.classList.remove('active');
    });

    // PASO 3: Mostrar la sección seleccionada
    // getElementById busca el elemento HTML que tenga ese ID específico
    const seccionSeleccionada = document.getElementById(tabId);
    
    // Si encontramos la sección, le agregamos la clase 'active' para mostrarla
    if (seccionSeleccionada) {
        seccionSeleccionada.classList.add('active');
    }

    // PASO 4: Activar el botón que fue presionado
    // 'event.target' representa el elemento que disparó el evento (el botón clickeado)
    const botonClickeado = event.target;
    botonClickeado.classList.add('active');

    // BONUS: Scroll suave hacia arriba para mejor experiencia de usuario
    // Esto hace que la página se desplace suavemente al inicio
    window.scrollTo({
        top: 0,              // Posición: arriba de todo
        behavior: 'smooth'   // Comportamiento: desplazamiento suave
    });

    // Mensaje en consola para debugging (puedes verlo con F12 en el navegador)
}


// ============================================
// FUNCIONALIDAD 2: VALIDACIÓN DE FORMULARIO
// ============================================

/**
 * Función que valida el formulario antes de enviarlo al servidor
 * Se ejecuta cuando el usuario intenta enviar el formulario (evento onsubmit)
 * 
 * @returns {boolean} - true si todo es válido (permite envío), false si hay errores (bloquea envío)
 * 
 * Validaciones que realiza:
 * - Nombre: mínimo 3 caracteres
 * - Email: formato correcto (algo@algo.algo)
 * - Mensaje: mínimo 10 caracteres
 */
function validarFormulario() {
    // Variable para controlar si el formulario es válido
    let formularioEsValido = true;

    // ----------------------------------------
    // OBTENER VALORES DE LOS CAMPOS
    // ----------------------------------------
    
    // Obtenemos el elemento input con id="nombre"
    const campoNombre = document.getElementById('nombre');
    // Obtenemos su valor y removemos espacios al inicio/final con trim()
    const valorNombre = campoNombre.value.trim();

    // Lo mismo para email
    const campoEmail = document.getElementById('email');
    const valorEmail = campoEmail.value.trim();

    // Y para mensaje
    const campoMensaje = document.getElementById('mensaje');
    const valorMensaje = campoMensaje.value.trim();

    // ----------------------------------------
    // OBTENER ELEMENTOS DE ERROR (para mostrar mensajes)
    // ----------------------------------------
    
    const errorNombre = document.getElementById('errorNombre');
    const errorEmail = document.getElementById('errorEmail');
    const errorMensaje = document.getElementById('errorMensaje');

    // ----------------------------------------
    // RESETEAR MENSAJES DE ERROR
    // ----------------------------------------
    // Ocultamos todos los mensajes de error antes de validar
    errorNombre.style.display = 'none';
    errorEmail.style.display = 'none';
    errorMensaje.style.display = 'none';

    // Restauramos el color de los bordes a su estado normal
    campoNombre.style.borderColor = '#667eea';
    campoEmail.style.borderColor = '#667eea';
    campoMensaje.style.borderColor = '#667eea';

    // ----------------------------------------
    // VALIDACIÓN 1: NOMBRE (mínimo 3 caracteres)
    // ----------------------------------------
    
    if (valorNombre.length < 3) {
        // Si el nombre tiene menos de 3 caracteres, mostramos el error
        errorNombre.style.display = 'block';
        campoNombre.style.borderColor = 'red';
        formularioEsValido = false;
    } else {
        // Si es válido, ponemos el borde verde
        campoNombre.style.borderColor = 'green';
    }

    // ----------------------------------------
    // VALIDACIÓN 2: EMAIL (formato correcto)
    // ----------------------------------------
    
    // Expresión regular (regex) para validar formato de email
    // Explicación: debe tener algo@algo.algo
    const expresionRegularEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    // test() verifica si el email cumple con el patrón
    if (!expresionRegularEmail.test(valorEmail)) {
        // Si NO cumple el formato, mostramos error
        errorEmail.style.display = 'block';
        campoEmail.style.borderColor = 'red';
        formularioEsValido = false;
    } else {
        // Si cumple, borde verde
        campoEmail.style.borderColor = 'green';
    }

    // ----------------------------------------
    // VALIDACIÓN 3: MENSAJE (mínimo 10 caracteres)
    // ----------------------------------------
    
    if (valorMensaje.length < 10) {
        // Si el mensaje es muy corto, mostramos error
        errorMensaje.style.display = 'block';
        campoMensaje.style.borderColor = 'red';
        formularioEsValido = false;
    } else {
        // Si es válido, borde verde
        campoMensaje.style.borderColor = 'green';
    }

    // ----------------------------------------
    // RESULTADO FINAL DE LA VALIDACIÓN
    // ----------------------------------------
    
    if (formularioEsValido) {
        // Si TODO es válido, mostramos mensaje de éxito
        mostrarMensajeExito();
        
        // NOTA: Cuando conectes con Python, el formulario se enviará automáticamente
        // Por ahora retornamos true para permitir el envío
        return true;
    } else {
        // Si hay errores, bloqueamos el envío
        return false;
    }
}


/**
 * Función auxiliar para mostrar mensaje de éxito
 * Muestra un mensaje verde de confirmación y lo oculta después de 5 segundos
 */
function mostrarMensajeExito() {
    // Obtenemos el div del mensaje de éxito
    const mensajeExito = document.getElementById('mensajeExito');
    
    // Lo hacemos visible
    mensajeExito.style.display = 'block';

    // Configuramos un temporizador para ocultarlo después de 5 segundos
    setTimeout(function() {
        mensajeExito.style.display = 'none';
    }, 5000); // 5000 milisegundos = 5 segundos

}


// ============================================
// FUNCIONALIDAD EXTRA: VALIDACIÓN EN TIEMPO REAL
// ============================================

/**
 * Esta función se ejecuta cuando la página termina de cargar
 * Agrega listeners (escuchadores) a los campos para validar mientras el usuario escribe
 */
document.addEventListener('DOMContentLoaded', function() {
    // Añadir esto dentro de document.addEventListener('DOMContentLoaded', function() { ... })

    // Detectar si venimos de un envío exitoso (URL contiene ?envio=exito)
    const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.get('envio') === 'exito') {
             mostrarMensajeExito();
            // Limpiar la URL para que no salga el mensaje al refrescar
            window.history.replaceState({}, document.title, "/");
        }
    // DOMContentLoaded se dispara cuando todo el HTML está cargado y listo

    // ----------------------------------------
    // VALIDACIÓN EN TIEMPO REAL - NOMBRE
    // ----------------------------------------
    
    const campoNombre = document.getElementById('nombre');
    
    // Verificamos que el campo existe antes de agregar el listener
    if (campoNombre) {
        // 'input' es el evento que se dispara cada vez que el usuario escribe
        campoNombre.addEventListener('input', function() {
            // 'this' se refiere al elemento que disparó el evento (el input)
            if (this.value.trim().length >= 3) {
                // Si cumple la validación, borde verde
                this.style.borderColor = 'green';
            } else {
                // Si no cumple, borde normal (no rojo para no molestar)
                this.style.borderColor = '#667eea';
            }
        });
    }

    // ----------------------------------------
    // VALIDACIÓN EN TIEMPO REAL - EMAIL
    // ----------------------------------------
    
    const campoEmail = document.getElementById('email');
    
    if (campoEmail) {
        campoEmail.addEventListener('input', function() {
            const expresionRegularEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            
            if (expresionRegularEmail.test(this.value.trim())) {
                this.style.borderColor = 'green';
            } else {
                this.style.borderColor = '#667eea';
            }
        });
    }

    // ----------------------------------------
    // VALIDACIÓN EN TIEMPO REAL - MENSAJE
    // ----------------------------------------
    
    const campoMensaje = document.getElementById('mensaje');
    
    if (campoMensaje) {
        campoMensaje.addEventListener('input', function() {
            if (this.value.trim().length >= 10) {
                this.style.borderColor = 'green';
            } else {
                this.style.borderColor = '#667eea';
            }
        });
    }

    // ----------------------------------------
    // ANIMACIÓN DE ENTRADA (OPCIONAL)
    // ----------------------------------------
    
    // Pequeña animación para el header cuando carga la página
    const header = document.querySelector('header');
    if (header) {
        header.style.opacity = '0';
        header.style.transform = 'translateY(-20px)';
        header.style.transition = 'opacity 0.8s ease, transform 0.8s ease';

        // Después de 100ms, lo hacemos aparecer
        setTimeout(function() {
            header.style.opacity = '1';
            header.style.transform = 'translateY(0)';
        }, 100);
    }

    // Animación progresiva para los botones de navegación
    const botones = document.querySelectorAll('.botondePestaña');
    botones.forEach(function(boton, indice) {
        boton.style.opacity = '0';
        boton.style.transform = 'translateY(20px)';
        boton.style.transition = 'opacity 0.5s ease, transform 0.5s ease';

        // Cada botón aparece con un pequeño retraso (efecto cascada)
        setTimeout(function() {
            boton.style.opacity = '1';
            boton.style.transform = 'translateY(0)';
        }, 300 + (indice * 100)); // 300ms base + 100ms por cada botón
    });

});


// ============================================
// NOTAS FINALES PARA EL ESTUDIANTE
// ============================================

/*
 * RESUMEN DE FUNCIONALIDADES IMPLEMENTADAS:
 * 
 * ✅ 1. NAVEGACIÓN ENTRE PESTAÑAS (showTab)
 *    - Cambia dinámicamente entre secciones sin recargar
 *    - Actualiza la clase 'active' de botones y secciones
 *    - Scroll suave hacia arriba
 * 
 * ✅ 2. VALIDACIÓN DE FORMULARIO (validarFormulario)
 *    - Valida nombre (3+ caracteres)
 *    - Valida email (formato correcto)
 *    - Valida mensaje (10+ caracteres)
 *    - Muestra errores visuales
 *    - Bloquea envío si hay errores
 * 
 * ✅ EXTRA: VALIDACIÓN EN TIEMPO REAL
 *    - Los campos se validan mientras el usuario escribe
 *    - Feedback visual inmediato (bordes verdes)
 * 
 * ✅ EXTRA: ANIMACIONES
 *    - Entrada animada del header
 *    - Aparición progresiva de botones
 * 
 * PARA PROBARLO:
 * 1. Abre la consola del navegador (F12)
 * 2. Verás mensajes de log cuando interactúes con la página
 * 3. Intenta enviar el formulario con datos inválidos
 * 4. Prueba escribir en los campos y ver la validación en tiempo real
 * 
 * PRÓXIMO PASO:
 * - Crear el backend en Python para recibir los datos del formulario
 * - Guardar los datos en MySQL
 * - Crear la página de administración protegida
 */