@echo off
echo Testing FinSolve RAG Chatbot
echo.

echo Testing Login...
curl.exe -X GET "http://127.0.0.1:8000/login" -u "Tony:password123"
echo.

echo Testing Chat - General Question...
curl.exe -X POST "http://127.0.0.1:8000/chat" -u "Tony:password123" -H "Content-Type: application/json" -d "{\"message\":\"What is FinSolve Technologies?\"}"
echo.

echo Testing Chat - Engineering Question...
curl.exe -X POST "http://127.0.0.1:8000/chat" -u "Tony:password123" -H "Content-Type: application/json" -d "{\"message\":\"What technologies does FinSolve use?\"}"
echo.

echo Testing Chat - Finance Question...
curl.exe -X POST "http://127.0.0.1:8000/chat" -u "Sam:financepass" -H "Content-Type: application/json" -d "{\"message\":\"What was the revenue growth in 2024?\"}"
echo.

echo Testing Chat - Marketing Question...
curl.exe -X POST "http://127.0.0.1:8000/chat" -u "Bruce:securepass" -H "Content-Type: application/json" -d "{\"message\":\"Tell me about our Q4 marketing results\"}"
echo.

echo Testing Chat - HR Question...
curl.exe -X POST "http://127.0.0.1:8000/chat" -u "Natasha:hrpass123" -H "Content-Type: application/json" -d "{\"message\":\"How many employees do we have?\"}"
echo.

echo All tests completed!
pause