import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import ScannerView from '../ScannerView.vue'

// Mock frappe-ui's createResource
const mockCreateResource = vi.fn()
vi.mock('frappe-ui', () => ({
  createResource: (opts: any) => {
    mockCreateResource(opts)
    return {
      submit: vi.fn(),
      fetch: vi.fn(),
      loading: false,
      data: null,
      promise: Promise.resolve()
    }
  }
}))

// Mock Child Components
const ScannerLoginStub = {
    template: '<div data-testid="scanner-login"></div>',
    props: ['loading', 'error']
}
const ScannerScheduleListStub = {
    template: '<div data-testid="scanner-schedule-list"></div>',
    props: ['loading', 'schedules']
}
const ScannerActiveStub = {
    template: '<div data-testid="scanner-active"></div>',
    props: ['schedule', 'history', 'result', 'showResultModal', 'autoCloseTimer', 'loading']
}

describe('ScannerView.vue', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('initializes basic resources on mount', () => {
    mount(ScannerView, {
      global: {
        stubs: {
          ScannerLogin: ScannerLoginStub,
          ScannerScheduleList: ScannerScheduleListStub,
          ScannerActive: ScannerActiveStub
        }
      }
    })
    
    // Check if resources were created
    // We expect multiple calls: userResource, rolesResource, schedulesResource, loginResource, checkinResource
    expect(mockCreateResource).toHaveBeenCalled()
  })

  it('configures checkinResource correctly', async () => {
    const wrapper = mount(ScannerView, {
      global: {
        stubs: {
          ScannerLogin: ScannerLoginStub,
          ScannerScheduleList: ScannerScheduleListStub,
          ScannerActive: ScannerActiveStub
        }
      }
    })

    // Find the call that corresponds to checkinResource
    const checkinCall = mockCreateResource.mock.calls.find((args: any[]) => 
        args[0].url === 'ticketed_event.ticketed_event.doctype.event_registration.event_registration.check_in_participant'
    )
    expect(checkinCall).toBeDefined()
    const checkinOptions = checkinCall[0]

    // --- Test makeParams ---
    // At default, viewState is 'login', currentSchedule is null.
    // We need to transition state to set currentSchedule to test makeParams fully.

    // Force verify getting into 'scanning' state
    // 1. Trigger login success (simulated by manually setting viewState or mocking user/role success)
    // Since viewState is local, we can't easily set it without exposing it.
    // BUT we can interact with the component via emitted events from stubs?
    // Wait, the stubs are in v-if blocks.
    // Initially 'login' matches.
    
    // Simulate Login Success flow if we want to change state "naturally":
    // loginResource.onSuccess -> userResource.fetch -> rolesResource.fetch -> viewState = 'select_schedule'
    // This is complex to coordinate via mocks.
    
    // ALTERNATIVE: Use vm (internal instance) to set state if allowed by test-utils, 
    // BUT <script setup> is closed by default.
    // However, we can simulate the "flow" by calling the callbacks captured by our mock.

    // 1. Get rolesResource options
    const rolesCall = mockCreateResource.mock.calls.find((args: any[]) => args[0].url.includes('get_roles'))
    const rolesOptions = rolesCall[0]
    
    // Simulate Administrator role to unlock 'select_schedule'
    rolesOptions.onSuccess(['Scanner'])
    await wrapper.vm.$nextTick()
    
    // Now we should be in 'select_schedule' mode
    expect(wrapper.findComponent(ScannerScheduleListStub).exists()).toBe(true)
    
    // 2. Select a schedule
    const mockSchedule = { name: 'SCH-001', date: '2025-01-01' }
    wrapper.findComponent(ScannerScheduleListStub).vm.$emit('select', mockSchedule)
    await wrapper.vm.$nextTick()
    
    // Now we should be in 'scanning' mode
    expect(wrapper.findComponent(ScannerActiveStub).exists()).toBe(true)
    
    // --- Verify makeParams ---
    const params = checkinOptions.makeParams('QR-123')
    expect(params).toEqual({
        qr_code_id: 'QR-123',
        schedule: 'SCH-001'
    })

    // --- Verify onSuccess ---
    const mockSuccessData = {
        participant: 'John Doe',
        schedule: 'SCH-001',
        time: '12:00'
    }
    
    checkinOptions.onSuccess(mockSuccessData)
    await wrapper.vm.$nextTick()

    // Verify result is passed to ScannerActive
    const activeComp = wrapper.findComponent(ScannerActiveStub)
    expect(activeComp.props('result')).toMatchObject({
        status: 'success',
        participant: 'John Doe',
        schedule: 'SCH-001'
    })
    expect(activeComp.props('showResultModal')).toBe(true)

    // --- Verify onError ---
    const mockError = { message: 'Already checked in' }
    checkinOptions.onError(mockError)
    await wrapper.vm.$nextTick()
    
    expect(activeComp.props('result')).toMatchObject({
        status: 'error',
        message: 'Already checked in'
    })
  })
})
