# Audio Recording & Native S2T (Mi Recuerdo Vivo)

We propose an architecture where the mobile app records the audio and then sequentially uses the device's native S2T to transcribe it. Then, both resources (audio file + text) are sent to the backend in a single request. The backend stores the file in Supabase Storage and saves the structured text in the database.

## User Review Required

> [!IMPORTANT]
> **Expo & Native S2T**: Using native Speech-to-Text requires native modules that are **not included in Expo Go**. The npm plugin only contains the JavaScript bridge, but requires the iOS/Android native source code to access the voice engines. We must install this plugin and compile a Custom Dev Client (`expo run:android` / `expo run:ios`). This means you will stop using the standard "Expo Go" app and use a custom development build of your app.

> [!IMPORTANT]
> **Render Limits (Free Tier)**: Sending heavy audio files in a single HTTP request could cause a timeout if Render is experiencing a "cold start" or if the file is too large. **We have established a strict limit of 3 minutes of recording.**

## Proposed Changes

---

### Mobile App (`living-memories-mobile`)

#### [MODIFY] `package.json`
- Install `expo-av` for audio recording.
- Install a file-specialized native S2T plugin, such as `expo-speech-transcriber` (or alternatively `whisper.rn` to run Whisper locally and for free on the device).

#### [NEW] `src/data/network/memoriesApiClient.ts`
- Create the network call `uploadMemory` using `multipart/form-data` to send the `.m4a`/`.wav` file along with the `transcribedText`.

#### [NEW] `src/domain/memories/useCases/RecordMemoryUseCase.ts`
- Implement the UseCase that orchestrates sending the data using the memories repository.

#### [NEW] `src/presentation/viewModels/home/useRecordingViewModel.ts`
- Create the ViewModel to handle microphone permissions.
- Control the lifecycle of `expo-av` (start, stop, limit to **3 minutes max**).
- Upon finishing the recording, take the saved `.m4a` file and pass it to the native S2T for sequential local transcription.

#### [MODIFY] `src/presentation/components/home/RecordButton.tsx`
- Connect the UI button to invoke `startRecording` and `stopRecording` from the ViewModel.
- Show a "Listening..." visual state.

---

### Backend API (`living-memories-api`)

#### [NEW] `app/features/memories/schemas.py`
- Pydantic models for the memory creation response (`MemoryResponse`).

#### [NEW] `app/features/memories/router.py`
- Endpoint `POST /api/v1/memories/upload`.
- Uses `fastapi.UploadFile` for the audio and `fastapi.Form()` to receive the `transcribed_text`.

#### [NEW] `app/features/memories/service.py`
- **1. Storage**: Upload the audio file to `Supabase Storage` (bucket: `memories`) and generate a public/private URL.
- **2. Processing**: (Initial mock) Extract tags and a title from the transcribed text (future NLP/LLM integration).
- **3. Database**: Save the entity in Supabase DB.

#### [NEW] `app/features/memories/repository.py`
- Insert logic for the `memories` table in Supabase, saving both the text and the `audio_url`.

## Verification Plan

### Automated Tests
- **Mobile**: Add unit tests (Jest) for the recording ViewModel, mocking `expo-av` and the S2T client.
- **API**: Add unit tests (pytest + httpx) for the `POST /upload` endpoint, mocking Supabase Storage and DB to prevent real connections.

### Manual Verification
- **Physical Device**: S2T (especially dictation) usually does not work well on iOS simulators. It will require testing on a physical iPhone or Android.
- Record a 10-second memory.
- Verify in Supabase Storage that the audio file uploaded correctly and is playable.
- Verify in the database that the transcribed text was saved correctly.
