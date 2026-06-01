# NQ Market Calendar....

**Tu calendario económico automatizado para el Nasdaq 100 (NQ).**

Sin gastar tokens de IA. Sin depender de tu computadora. Funciona solo en la nube y se actualiza automático varias veces al día.

---

## ¿Qué hace esto?

Es una **página web** (como Facebook o Google) que abres desde tu celular o computadora y te dice:

- 📅 **Qué noticias macro vienen hoy y esta semana** (CPI, NFP, FOMC, PMI, PCE, GDP, etc.)
- 📊 **Cómo afectan al NQ / Tech** con 3 escenarios: alcista, bajista, neutral
- 📈 **Earnings de las Big Tech** (AAPL, NVDA, MSFT, etc.)
- 🧠 **Contexto ICT** para que sepas dónde buscar en el chart post-noticia

Todo esto se llena **solo**, sin que tú hagas nada.

---

## ¿Qué necesito? (2 cosas gratis)

1. Una cuenta en **GitHub** (como crear cuenta en Instagram, gratis).
2. Una **API Key gratis** de Finnhub (es como una contraseña para que el sistema pida datos).

---

## PASO 1: Obtener tu API Key de Finnhub (gratis)

Finnhub es una empresa que nos presta datos de calendario económico y earnings. Necesitamos una "llave" para pedir esos datos.

1. Ve a [https://finnhub.io](https://finnhub.io)
2. Arriba a la derecha haz clic en **"Get free api key"**
3. Regístrate con tu email y una contraseña
4. Te mandan un email para confirmar — ábrelo y haz clic en el link
5. Una vez dentro, verás una página que dice **API Key** con un código largo tipo `c123abc456def...`
6. **Cópialo y guárdalo en un bloc de notas de tu celular o computadora**. Lo usaremos en el Paso 4.

> 💡 **Analogía:** La API Key es como el número de tarjeta de un gimnasio. Con ese número, la máquina (nuestro calendario) puede entrar y traer los datos.

---

## PASO 2: Crear tu repositorio en GitHub

GitHub es como Google Drive, pero para proyectos de código. Ahí guardaremos tu calendario y GitHub lo servirá como página web.

1. Ve a [https://github.com](https://github.com) e inicia sesión (o crea cuenta si no tienes).
2. Arriba a la derecha haz clic en el **+** y luego **"New repository"**.
3. En **Repository name** escribe: `nq-market-calendar`
4. Deja todo como está (público está bien, no hay información privada aquí).
5. Haz clic en el botón verde **"Create repository"**.

Ya tienes tu "carpeta" en la nube.

---

## PASO 3: Subir los archivos del calendario

Ahora vamos a meter dentro de esa carpeta todos los archivos que yo te di.

1. Dentro de tu nuevo repo verás un mensaje que dice **"Quick setup"**. Abajo hay un link que dice **"uploading an existing file"**. Haz clic ahí.
2. Se abre una zona para arrastrar archivos. 
3. Ve a la carpeta donde tengas estos archivos (los que te di) y **arrastra TODA la carpeta `nq-market-calendar` completa**.
   - Si no deja arrastrar carpetas, entonces entra a cada subcarpeta y sube los archivos uno por uno:
     - `index.html`
     - `css/style.css`
     - `js/app.js`
     - `data/calendar.json`
     - `scripts/update_calendar.py`
     - `scripts/requirements.txt`
     - `.github/workflows/update-calendar.yml`
4. Bajo de todo donde dice **"Commit changes"**, escribe un mensaje (puede ser "Mi calendario NQ") y haz clic en **"Commit changes"**.

Ahora tus archivos viven en la nube de GitHub.

---

## PASO 4: Esconder tu API Key (muy importante)

No queremos que la API Key de Finnhub quede visible para todo el mundo. Vamos a guardarla en un lugar secreto dentro de GitHub.

1. Dentro de tu repo, arriba hay un menú: **Settings** (última pestaña).
2. En el menú lateral izquierdo, busca y haz clic en **"Secrets and variables" → "Actions"**.
3. Haz clic en el botón verde **"New repository secret"**.
4. En **Name** escribe exactamente: `FINNHUB_API_KEY`
5. En **Secret** pega la API Key que copiaste en el Paso 1.
6. Haz clic en **"Add secret"**.

Listo. Tu llave está guardada de forma segura.

---

## PASO 5: Activar la página web (GitHub Pages)

Ahora le decimos a GitHub: "Quiero que esta carpeta se vea como una página web pública".

1. Dentro de tu repo, haz clic en **Settings**.
2. En el menú lateral izquierdo, baja hasta **"Pages"** y haz clic.
3. En **Branch** selecciona `main` y en la carpeta de al lado selecciona `/(root)`.
4. Haz clic en **"Save"**.
5. Espera 1–2 minutos. Recarga la página.
6. Arriba te aparecerá un mensaje verde con una URL tipo:
   `https://tunombre.github.io/nq-market-calendar/`
   
   ¡Esa es tu página! Ábrela en el celular o PC y verás tu calendario.

---

## PASO 6: Activar la actualización automática

El sistema ya está configurado para actualizarse solo, pero necesitamos que GitHub Actions tenga permiso para escribir.

1. En tu repo, haz clic en la pestaña **Settings**.
2. En el menú lateral izquierdo, haz clic en **"Actions" → "General"**.
3. Baja hasta **"Workflow permissions"**.
4. Selecciona **"Read and write permissions"**.
5. Haz clic en **Save**.

---

## ¿Cómo funciona la magia?

- **Cada 6 horas** (00:00, 06:00, 12:00, 18:00 UTC), la "nube" de GitHub despierta y ejecuta el script Python.
- El script pide datos a Finnhub (noticias macro y earnings de tech).
- El script aplica las reglas de impacto al NQ que están programadas.
- Guarda todo en el archivo `data/calendar.json`.
- Tu página web lee ese archivo y lo muestra bonito.
- **Tú no haces nada.** Solo abres la URL.

Si quieres forzar una actualización manual:
1. Ve a tu repo → pestaña **Actions**.
2. Haz clic en el workflow **"Update NQ Calendar"**.
3. Arriba a la derecha haz clic en **"Run workflow"** → **"Run workflow"**.
4. Espera 30 segundos y recarga tu página web.

---

## Estructura de archivos (para curiosos)

```
nq-market-calendar/
├── index.html          ← La página web que tú ves
├── css/style.css       ← Los colores y diseño oscuro
├── js/app.js           ← La lógica de los botones y tarjetas
├── data/calendar.json  ← Los datos generados automáticamente
├── scripts/
│   ├── update_calendar.py   ← El cerebro que pide datos a Finnhub
│   └── requirements.txt     ← Qué necesita el cerebro
└── .github/workflows/
    └── update-calendar.yml  ← El despertador automático cada 6h
```

---

## Si algo sale mal (solución de problemas)

**La página muestra "No se pudo cargar el calendario"**
- Ve al Paso 5 y verifica que GitHub Pages esté activo.
- Asegúrate de que el archivo `data/calendar.json` exista en tu repo.

**No aparecen eventos nuevos**
- Ve a la pestaña **Actions** de tu repo y mira si el workflow tiene una ✅ verde. Si tiene una ❌ roja, haz clic para ver el error.
- Verifica que tu API Key esté bien escrita en Secrets (Paso 4).

**Los horarios no coinciden**
- El script usa ET (Nueva York) y CO (Colombia ET−1h). Finnhub no siempre incluye la hora exacta; algunos eventos pueden aparecer sin hora. Eso es normal para eventos aún no confirmados.

---

## Costo

**$0.00**. GitHub Pages es gratis. GitHub Actions es gratis para repos públicos (hasta 2,000 minutos al mes, suficiente). Finnhub free tier es gratis (60 peticiones por minuto, suficiente para cada 6 horas).

---

## Nota legal

Esta herramienta es solo para **información educativa**. No es asesoría financiera. Siempre verifica datos críticos en fuentes oficiales antes de operar con dinero real.

---

¿Preguntas? Revisa los Pasos 1–6 con calma. Si te trabas en alguno, dime exactamente en qué paso y qué mensaje de error ves.
