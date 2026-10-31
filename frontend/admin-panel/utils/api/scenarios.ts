import { http } from './httpClient'
import type { Scenario, ScenarioInput, ScenarioPage } from '~/types/scenario'

export const getScenarios = (objectId: string, skip = 0) => http<ScenarioPage>('/scenarios/?' + new URLSearchParams({ object_id: objectId, skip: String(skip), limit: '50' }))
export const getScenario = (id: string) => http<Scenario>('/scenarios/' + encodeURIComponent(id))
export const createScenario = (data: ScenarioInput) => http<Scenario>('/scenarios/', { method: 'POST', body: JSON.stringify(data) })
export const updateScenario = (id: string, data: ScenarioInput, revision: number) => http<Scenario>('/scenarios/' + encodeURIComponent(id), { method: 'PUT', body: JSON.stringify({ ...data, expected_revision: revision }) })
export const toggleScenario = (scenario: Scenario) => http<Scenario>('/scenarios/' + encodeURIComponent(scenario.id), { method: 'PATCH', body: JSON.stringify({ enabled: !scenario.enabled, expected_revision: scenario.revision }) })
export const deleteScenario = (scenario: Scenario) => http<void>(`/scenarios/${encodeURIComponent(scenario.id)}?expected_revision=${scenario.revision}`, { method: 'DELETE' })
