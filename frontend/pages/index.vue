<script setup>
import { DateFormatter, getLocalTimeZone, today } from '@internationalized/date'

const baseURL = useRuntimeConfig().public.baseUrl
const df = new DateFormatter('zh-CN')
const stock_code = ref('000001')
const days = ref(30)
const end_date1 = ref(today(getLocalTimeZone()))
const content = ref('')

async function analyse1() {
    var url = '/api/stock_analyse'
    var j = {
        code: stock_code.value
    }
    if (days.value) {
        j.days = days.value
    }
    if (end_date1.value) {
        j.end_date = end_date1.value.toString().replaceAll('-', '')
    }
    const response = await $fetch(url, {
        baseURL: baseURL,
        headers: {
            'Content-Type': 'application/json'
        },
        method: 'POST',
        body: JSON.stringify(j),
        responseType: 'stream'
    }
    )
    const reader = response.getReader()
    const decoder = new TextDecoder()
    content.value = ''
    while (true) {
        const { done, value } = await reader.read()
        if (done) break
        content.value += decoder.decode(value)
    }
}

</script>

<template>
    <div class="min-h-screen bg-gray-100">
        <div class="mx-auto pt-16 max-w-4xl">
            <UCard>
                <div class="space-y-3 px-4">
                    <div class="text-center text-3xl font-bold">Stock Analyst</div>
                    <UButtonGroup>
                        <UBadge color="neutral" variant="outline" label="Stock Code"></UBadge>
                        <UInput v-model="stock_code"></UInput>
                    </UButtonGroup>
                    <div class="flex space-x-4">
                        <UButtonGroup>
                            <UBadge color="neutral" variant="outline" label="days"></UBadge>
                            <UInput v-model="days"></UInput>
                        </UButtonGroup>
                        <UButtonGroup>
                            <UBadge color="neutral" variant="outline" label="End Date"></UBadge>
                            <UPopover>
                                <UButton color="neutral" variant="subtle" icon="i-lucide-calendar">
                                    {{ end_date1 ? df.format(end_date1.toDate(getLocalTimeZone())) : 'Select Date' }}
                                </UButton>
                                <template #content>
                                    <UCalendar v-model="end_date1" />
                                </template>
                            </UPopover>
                        </UButtonGroup>
                        <UButton @click="analyse1">Analyse</UButton>
                    </div>
                    <div class="w-full max-w-none min-h-50 px-2 prose bg-gray-100 border-2">
                        <MDC :value="content"></MDC>
                    </div>
                </div>
            </UCard>
        </div>
    </div>
</template>