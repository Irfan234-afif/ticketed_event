import { defineStore } from "pinia";
import { createResource, createListResource } from "frappe-ui";
import { reactive, ref, computed } from "vue";
import { useRouter } from "vue-router";

interface Participant {
  full_name: string;
  email: string;
  phone: string;
  instagram: string;
}

interface UserData {
  full_name: string;
  email: string;
  phone: string;
}

export const useRegistrationStore = defineStore("registration", () => {
  const router = useRouter();

  // State
  const currentStep = ref(1);
  const eventId = ref<string | null>(null);

  // Data State
  const event = ref<any>(null);
  const user = reactive<UserData>({
    full_name: "",
    email: "",
    phone: "",
  });

  const participants = ref<Participant[]>([]);

  const selectedDate = ref<{ date: string; title: string } | null>(null);
  const selectedSchedules = ref<string[]>([]);
  const captchaToken = ref<string>("");
  const validationErrors = ref<string[]>([]);
  const termsAccepted = ref(false);
  const recaptchaSiteKey = ref<string>("");

  // Resources
  const settingsResource = createResource({
    url: "ticketed_event.api.get_settings",
    auto: false,
    onSuccess(data: any) {
      if (data.google_recaptcha_site_key) {
        recaptchaSiteKey.value = data.google_recaptcha_site_key;
      }
    },
  });

  const schedulesResource = createResource({
    url: "ticketed_event.api.get_event_schedules",
    auto: false,
  });

  const submitRegistration = createResource({
    url: "ticketed_event.ticketed_event.doctype.event_registration.event_registration.create_full_registration",
    makeParams(values: any) {
      return {
        event: eventId.value,
        schedules: JSON.stringify(selectedSchedules.value),
        user_data: JSON.stringify(user),
        participants: JSON.stringify(participants.value),
        captcha_token: captchaToken.value,
      };
    },
    onSuccess(data: any) {
      // Navigate to success
    },
    onError(error: any) {
      // Extract error messages
      if (error.messages && Array.isArray(error.messages)) {
        validationErrors.value = error.messages;
      } else if (error.message) {
        validationErrors.value = [error.message];
      } else {
        validationErrors.value = ["An error occurred during registration"];
      }
    },
  });

  // Actions
  function setEvent(id: string, data: any) {
    eventId.value = id;
    event.value = data;
    // Fetch schedules
    schedulesResource.submit({ event: id });
    // Fetch Global Settings (Captcha)
    settingsResource.fetch();
  }

  function addUserAsParticipant() {
    // Ensure the first participant matches the user if not edited
    if (participants.value.length === 0) {
      participants.value.push({
        full_name: user.full_name,
        email: user.email,
        phone: user.phone,
        instagram: "",
      });
    } else {
      // Update first participant if it matches user intent?
      // For now let's just keep them separate or initialize once.
      if (participants.value[0]?.email === user.email) {
        participants.value[0].full_name = user.full_name;
        participants.value[0].phone = user.phone;
      }
    }
  }

  function addParticipant() {
    if (participants.value.length < 3) {
      participants.value.push({
        full_name: "",
        email: "",
        phone: "",
        instagram: "",
      });
    }
  }

  function removeParticipant(index: number) {
    if (participants.value.length > 1) {
      // Always keep at least one? Or allow 0 and rely on index 0 logic?
      // Requirement: "1 user bisa mengisi maximal 3 participant"
      // Usually implies at least 1.
      participants.value.splice(index, 1);
    }
  }

  function reset() {
    currentStep.value = 1;
    participants.value = [];
    selectedSchedules.value = [];
    selectedDate.value = null;
    user.email = "";
    user.full_name = "";
    user.phone = "";
    schedulesResource.data = [];
    validationErrors.value = []
    termsAccepted.value = false
  }

  function clearErrors() {
    validationErrors.value = [];
  }

  return {
    currentStep,
    eventId,
    event,
    user,
    participants,
    selectedDate,
    selectedSchedules,
    schedulesResource,
    submitRegistration,
    setEvent,
    addUserAsParticipant,
    addParticipant,
    removeParticipant,
    reset,
    captchaToken,
    validationErrors,
    clearErrors,
    termsAccepted,
    recaptchaSiteKey,
  };
});
