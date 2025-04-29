// utils/getStatusColor.ts

// Функция для выбора цвета текста (как в таблице)
export function getStatusColor(statusId: number) {
    if (statusId === 1) return '#FACC15'; // text-yellow-400
    if (statusId === 2) return '#60A5FA'; // text-blue-400
    if (statusId === 3) return '#34D399'; // text-green-400
    if (statusId === 4) return '#F87171'; // text-red-400
    if (statusId === 8) return '#FFFFFF'; // белый
    return '#64748B'; // text-gray-500
}