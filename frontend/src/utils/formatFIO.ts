export function formatFIO(fullName: string): string {
    const parts = fullName.split(' ');

    if (parts.length !== 3) {
        return fullName; // Если формат неправильный, возвращаем оригинальную строку
    }

    const surname = parts[0];
    const initials = `${parts[1][0]}.${parts[2][0]}.`;

    return `${surname} ${initials}`;
}