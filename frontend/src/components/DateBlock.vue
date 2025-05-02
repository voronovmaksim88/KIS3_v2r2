<script setup lang="ts">
import { computed } from 'vue';

// Определение типа входных данных для компонента
interface DateData {
  start_moment?: string | null;
  deadline_moment?: string | null;
  end_moment?: string | null;
}

// Определяем пропсы для компонента через деструктуризацию
const props = defineProps<{
  order: DateData | null;
  theme: string; // Не используется в текущей логике, но оставлен
  detailBlockClass: string;
  detailHeaderClass: string;
  tdBaseTextClass: string;
}>();

/**
 * Преобразует строку даты в формате ISO 8601 в локальную дату и время
 * @param isoDateString - Строка даты в формате ISO 8601 или null/undefined
 * @param includeHourAndMinute - Включать ли часы и минуты в результат (по умолчанию: true)
 * @param includeSeconds - Включать ли секунды в результат (по умолчанию: false)
 * @returns Отформатированная строка с локальными датой и временем
 */
function formatLocalDateTime(
    isoDateString: string | null | undefined,
    includeHourAndMinute: boolean = true,
    includeSeconds: boolean = false
): string {
  // Проверка на пустую строку или null/undefined
  if (!isoDateString) {
    return '';
  }

  try {
    // Создаем объект Date из строки ISO
    const date = new Date(isoDateString);

    // Проверяем, является ли дата валидной
    if (isNaN(date.getTime())) {
      console.error('Invalid date string:', isoDateString);
      return isoDateString; // Возвращаем исходную строку в случае ошибки
    }

    // ВАЖНО: Не применяем смещение часового пояса здесь,
    // так как ISO строка уже содержит информацию о поясе (или подразумевает UTC).
    // Date() парсит это корректно. Форматирование в ЛОКАЛЬНОЕ время
    // должно происходить при выводе компонентов (getFullYear, getMonth и т.д.)

    // Извлекаем компоненты даты (они будут локальными)
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');

    // Формируем строку с датой
    let formattedDate = `${year}-${month}-${day}`;

    // Добавляем часы и минуты, если необходимо
    if (includeHourAndMinute) {
      const hours = String(date.getHours()).padStart(2, '0');
      const minutes = String(date.getMinutes()).padStart(2, '0');
      formattedDate += ` ${hours}:${minutes}`;

      // Добавляем секунды, если они нужны и если включены часы/минуты
      if (includeSeconds) {
        const seconds = String(date.getSeconds()).padStart(2, '0');
        formattedDate += `:${seconds}`;
      }
    }

    return formattedDate;
  } catch (error) {
    console.error('Error formatting date:', error);
    return isoDateString; // Возвращаем исходную строку в случае ошибки
  }
}

// --- Новые функции для расчета разницы и форматирования ---

interface DateDifference {
  years: number;
  months: number;
  days: number;
  totalDays: number; // Общее количество дней для определения знака и случая "сегодня"
}

/**
 * Рассчитывает разницу между двумя датами в годах, месяцах и днях.
 * @param date1 - Первая дата (объект Date)
 * @param date2 - Вторая дата (объект Date)
 * @returns Объект с разницей {years, months, days, totalDays}
 */
function calculateDateDifference(date1: Date, date2: Date): DateDifference {
  const d1 = new Date(date1.getFullYear(), date1.getMonth(), date1.getDate());
  const d2 = new Date(date2.getFullYear(), date2.getMonth(), date2.getDate());

  const diffTime = d2.getTime() - d1.getTime();
  const totalDays = Math.round(diffTime / (1000 * 60 * 60 * 24)); // Округляем для случая "сегодня"

  // Определяем, какая дата раньше, для корректного расчета
  let startDate = d1 < d2 ? d1 : d2;
  let endDate = d1 < d2 ? d2 : d1;

  let years = endDate.getFullYear() - startDate.getFullYear();
  let months = endDate.getMonth() - startDate.getMonth();
  let days = endDate.getDate() - startDate.getDate();

  // Корректировка отрицательных значений
  if (days < 0) {
    // Берем дни из предыдущего месяца конечной даты
    const prevMonthEndDate = new Date(endDate.getFullYear(), endDate.getMonth(), 0);
    days += prevMonthEndDate.getDate();
    months--; // Уменьшаем количество месяцев, так как заняли дни
  }

  if (months < 0) {
    months += 12; // Добавляем 12 месяцев
    years--; // Уменьшаем количество лет
  }

  // Если даты были переданы в обратном порядке, totalDays будет отрицательным
  // years, months, days всегда положительны или 0 из-за startDate/endDate
  return { years, months, days, totalDays };
}

// Вспомогательные функции для склонения слов
function getYearsText(years: number): string {
  const lastDigit = years % 10;
  const lastTwoDigits = years % 100;
  if (lastTwoDigits >= 11 && lastTwoDigits <= 19) return 'лет';
  if (lastDigit === 1) return 'год';
  if (lastDigit >= 2 && lastDigit <= 4) return 'года';
  return 'лет';
}

function getMonthsText(months: number): string {
  const lastDigit = months % 10;
  const lastTwoDigits = months % 100;
  if (lastTwoDigits >= 11 && lastTwoDigits <= 19) return 'месяцев';
  if (lastDigit === 1) return 'месяц';
  if (lastDigit >= 2 && lastDigit <= 4) return 'месяца';
  return 'месяцев';
}

function getDaysText(days: number): string {
  const lastDigit = days % 10;
  const lastTwoDigits = days % 100;
  if (lastTwoDigits >= 11 && lastTwoDigits <= 19) return 'дней';
  if (lastDigit === 1) return 'день';
  if (lastDigit >= 2 && lastDigit <= 4) return 'дня';
  return 'дней';
}

/**
 * Форматирует разницу дат в строку "X лет, Y месяцев, Z дней"
 * @param diff - Объект DateDifference
 * @returns Отформатированная строка
 */
function formatRelativeTimeDetailed(diff: DateDifference): string {
  const parts: string[] = [];
  if (diff.years > 0) {
    parts.push(`${diff.years} ${getYearsText(diff.years)}`);
  }
  if (diff.months > 0) {
    parts.push(`${diff.months} ${getMonthsText(diff.months)}`);
  }
  // Показываем дни, только если нет лет и месяцев, или если они есть и дни не 0
  if (diff.days > 0 && (parts.length < 2 || (diff.years > 0 || diff.months > 0))) {
    parts.push(`${diff.days} ${getDaysText(diff.days)}`);
  }
  // Если все по нулям (или только дни = 0), но totalDays не 0 (редкий случай из-за округления)
  // Или если years/months есть, а days=0, показываем 0 дней для ясности? Решил не показывать.
  if (parts.length === 0 && diff.totalDays !== 0) {
    // Если разница меньше дня, но не 0
    return `менее дня`; // Или можно вернуть пустую строку, чтобы скобки не отображались
  }
  if (parts.length === 0 && diff.totalDays === 0) {
    return 'сегодня'; // Для случая дедлайна
  }


  return parts.join(', ');
}

// --- Обновленные вычисляемые свойства ---

const timeSinceCreation = computed((): DateDifference | null => {
  if (!props.order?.start_moment) return null;
  try {
    const startDate = new Date(props.order.start_moment);
    const now = new Date();
    if (isNaN(startDate.getTime())) return null;
    return calculateDateDifference(startDate, now);
  } catch {
    return null;
  }
});

const timeUntilDeadline = computed((): DateDifference | null => {
  if (!props.order?.deadline_moment) return null;
  try {
    const deadlineDate = new Date(props.order.deadline_moment);
    const now = new Date();
    if (isNaN(deadlineDate.getTime())) return null;
    return calculateDateDifference(now, deadlineDate); // Порядок важен для totalDays
  } catch {
    return null;
  }
});

const timeSinceCompletion = computed((): DateDifference | null => {
  if (!props.order?.end_moment) return null;
  try {
    const endDate = new Date(props.order.end_moment);
    const now = new Date();
    if (isNaN(endDate.getTime())) return null;
    return calculateDateDifference(endDate, now);
  } catch {
    return null;
  }
});

// Проверка, просрочен ли дедлайн (используем totalDays из timeUntilDeadline)
const isDeadlineOverdue = computed(() => {
  // totalDays отрицательный, если deadlineDate < now
  return timeUntilDeadline.value !== null && timeUntilDeadline.value.totalDays < 0;
});

</script>

<template>
  <div :class="detailBlockClass">
    <h4 :class="detailHeaderClass">Даты</h4>

    <table class="w-full border-none table-fixed border-collapse">
      <tbody>
      <tr>
        <td :class="tdBaseTextClass" class="text-left pr-2 align-top">
          создан:
        </td>
        <td :class="tdBaseTextClass" class="text-left align-top">
          {{ formatLocalDateTime(props.order?.start_moment, false) || 'не определено' }}
        </td>
        <td v-if="timeSinceCreation && (timeSinceCreation.years > 0 || timeSinceCreation.months > 0 || timeSinceCreation.days > 0)" class="text-xs text-gray-500 pl-2 text-left align-top">
          ({{ formatRelativeTimeDetailed(timeSinceCreation) }} назад)
        </td>
        <td v-else class="w-px"></td>
      </tr>

      <tr>
        <td :class="tdBaseTextClass" class="text-left pr-2 align-top">
          дедлайн:
        </td>
        <td :class="[tdBaseTextClass, 'text-left align-top']">
          {{ formatLocalDateTime(props.order?.deadline_moment, false) || 'не определено' }}
        </td>
        <td
            v-if="timeUntilDeadline !== null"
            class="text-xs pl-2 text-left align-top"
            :class="isDeadlineOverdue ? 'text-red-400' : 'text-gray-500'"
        >
          <template v-if="timeUntilDeadline.totalDays > 0">
            (через {{ formatRelativeTimeDetailed(timeUntilDeadline) }})
          </template>
          <template v-else-if="timeUntilDeadline.totalDays === 0">
            (сегодня)
          </template>
          <template v-else>
            (просрочен на {{ formatRelativeTimeDetailed(timeUntilDeadline) }})
          </template>
        </td>
        <td v-else class="w-px"></td>
      </tr>

      <tr v-if="props.order?.end_moment">
        <td :class="tdBaseTextClass" class="text-left pr-2 align-top">
          завершён:
        </td>
        <td :class="tdBaseTextClass" class="text-left align-top">
          {{ formatLocalDateTime(props.order?.end_moment, false) || 'не определено' }}
        </td>
        <td v-if="timeSinceCompletion && (timeSinceCompletion.years > 0 || timeSinceCompletion.months > 0 || timeSinceCompletion.days > 0)" class="text-xs text-gray-500 pl-2 text-left align-top">
          ({{ formatRelativeTimeDetailed(timeSinceCompletion) }} назад)
        </td>
        <td v-else class="w-px"></td>
      </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
table {
  border: none;
  border-collapse: collapse;
  /* table-layout: fixed; /* Убедитесь, что используется fixed layout */
  /* width: 100%; Если нужно на всю ширину */
}

table tr {
  /* height: 2rem; /* Убрал фикс. высоту, т.к. текст может переноситься */
  border: none;
  vertical-align: top; /* Выравнивание по верху строки */
}

table td {
  padding: 4px 0; /* Вертикальный отступ внутри ячеек */
  border: none;
  vertical-align: middle; /* Выравнивание по верху ячейки */
}


table td:nth-child(1) { width: 20%; }
table td:nth-child(2) { width: 20%; }
table td:nth-child(3) { width: 60%; }

/* Добавил класс для пустой ячейки, чтобы она не коллапсировала */
.w-px {
  width: 1px;
}

</style>
