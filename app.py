<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Presentación de Preguntas</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/tailwindcss/2.2.19/tailwind.min.js"></script>
    <style>
        .fade-in {
            animation: fadeIn 0.5s ease-in;
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        .logo-container {
            aspect-ratio: 1;
            background: #2d3748;
            border-radius: 1rem;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
        }
        .logo-preview {
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
        }
    </style>
</head>
<body class="bg-gray-900 min-h-screen p-4 md:p-8">
    <div class="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-8">
        <!-- Panel Logo -->
        <div class="bg-gray-800 rounded-xl p-6 flex flex-col items-center">
            <button onclick="document.getElementById('logoInput').click()" 
                    class="mb-4 bg-blue-600 hover:bg-blue-700 text-white w-12 h-12 rounded-full flex items-center justify-center transition-colors">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="12" y1="5" x2="12" y2="19"></line>
                    <line x1="5" y1="12" x2="19" y2="12"></line>
                </svg>
            </button>
            <input type="file" id="logoInput" accept="image/*" class="hidden" onchange="handleLogoUpload(event)">
            <div id="logoContainer" class="logo-container w-full">
                <p class="text-gray-400">Área del Logo</p>
            </div>
        </div>

        <!-- Panel Preguntas -->
        <div class="bg-white rounded-xl p-6 flex flex-col min-h-[500px]">
            <div class="flex-grow flex flex-col items-center justify-center p-8">
                <div id="questionContainer" class="text-center">
                    <button onclick="document.getElementById('txtInput').click()"
                            class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg flex items-center gap-2">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                            <polyline points="17 8 12 3 7 8"></polyline>
                            <line x1="12" y1="3" x2="12" y2="15"></line>
                        </svg>
                        Cargar Preguntas
                    </button>
                    <input type="file" id="txtInput" accept=".txt" class="hidden" onchange="handleTxtUpload(event)">
                </div>
            </div>

            <!-- Navegación -->
            <div id="navigation" class="flex items-center justify-between px-4 hidden">
                <button onclick="previousQuestion()" id="prevBtn"
                        class="p-2 rounded-full bg-gray-800 text-white hover:bg-gray-700 disabled:bg-gray-200 disabled:text-gray-400">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="15 18 9 12 15 6"></polyline>
                    </svg>
                </button>
                <span id="counter" class="text-gray-600 font-medium"></span>
                <button onclick="nextQuestion()" id="nextBtn"
                        class="p-2 rounded-full bg-gray-800 text-white hover:bg-gray-700 disabled:bg-gray-200 disabled:text-gray-400">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="9 18 15 12 9 6"></polyline>
                    </svg>
                </button>
            </div>
        </div>
    </div>

    <script>
        let questions = [];
        let currentQuestion = 0;

        function handleLogoUpload(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const container = document.getElementById('logoContainer');
                    container.innerHTML = `<img src="${e.target.result}" class="logo-preview fade-in" alt="Logo">`;
                };
                reader.readAsDataURL(file);
            }
        }

        function handleTxtUpload(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    questions = e.target.result.split('\n').filter(q => q.trim());
                    if (questions.length > 0) {
                        currentQuestion = 0;
                        showQuestion();
                        document.getElementById('navigation').classList.remove('hidden');
                    }
                };
                reader.readAsText(file);
            }
        }

        function showQuestion() {
            const container = document.getElementById('questionContainer');
            container.innerHTML = `<h1 class="text-4xl font-bold text-gray-800 fade-in">${questions[currentQuestion]}</h1>`;
            updateNavigation();
        }

        function nextQuestion() {
            if (currentQuestion < questions.length - 1) {
                currentQuestion++;
                showQuestion();
            }
        }

        function previousQuestion() {
            if (currentQuestion > 0) {
                currentQuestion--;
                showQuestion();
            }
        }

        function updateNavigation() {
            document.getElementById('counter').textContent = `${currentQuestion + 1} / ${questions.length}`;
            document.getElementById('prevBtn').disabled = currentQuestion === 0;
            document.getElementById('nextBtn').disabled = currentQuestion === questions.length - 1;
        }
    </script>
</body>
</html>
