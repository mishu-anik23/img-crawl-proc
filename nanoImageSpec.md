# nanoImage - Project Specification

**Version:** 1.0.0  
**Date:** June 2026  
**Status:** Draft

---

## Table of Contents
1. [Introduction](#1-introduction)
2. [Technical Stack](#2-technical-stack)
3. [System Architecture](#3-system-architecture)
4. [Functional Requirements](#4-functional-requirements)
5. [API Endpoints](#5-api-endpoints)
6. [Database Schema](#6-database-schema-postgresql)
7. [Frontend Design](#7-frontend-design)
8. [Integration with Gemini Flash](#8-integration-with-gemini-flash)
9. [Image Generation Service Integration](#9-image-generation-service-integration)
10. [Implementation Plan](#10-implementation-plan-phase-wise)
11. [Non-Functional Requirements](#11-non-functional-requirements)
12. [Conclusion](#12-conclusion)
13. [Appendix](#13-appendix)

---

## 1. Introduction

**nanoImage** is a native web application centered around Google's **Gemini Flash** multimodal model. It enables users to upload single images or entire directory structures, apply a textual prompt, and leverage Gemini Flash's reasoning capabilities to generate **enhanced prompts** for a third‑party image generation API (e.g., Imagen, Stable Diffusion, DALL‑E). The final generated images are displayed in an aesthetically designed workspace that adapts to user‑defined business parameters, niches, and output styles.

### 1.1 Objectives
- Provide a seamless, professional‑grade tool for designers, marketers, and creators.
- Enable rapid generation and iteration on visual assets based on existing imagery and natural language instructions.
- Offer a highly customizable workspace that adapts to the user's specific domain and style preferences.

### 1.2 Target Users
- Graphic designers and creative professionals
- Marketing teams and social media managers
- Architects and real estate professionals
- E-commerce product photographers
- Content creators and artists

### 1.3 Key Differentiators
- **Native Gemini Integration**: Direct use of Gemini Flash for intelligent prompt engineering.
- **Directory Upload**: Preserve folder structures for batch processing workflows.
- **Adaptive Workspace**: The interface dynamically adjusts based on business model, niche, and style selections.
- **Preloaded Smart Suggestions**: Curated options with descriptions to guide users effectively.

---

## 2. Technical Stack

### 2.1 Backend (Python)

| Component | Choice | Rationale |
|-----------|--------|-----------|
| **Framework** | FastAPI | High performance, asynchronous support, automatic OpenAPI documentation, easy integration with Gemini and image generation APIs. |
| **Image Processing** | Pillow, OpenCV | For resizing, format conversion, and metadata extraction. |
| **File Handling** | aiofiles | Asynchronous file operations for directory uploads. |
| **Database ORM** | SQLAlchemy (async) | Robust, supports migrations, works well with FastAPI. |
| **Database** | PostgreSQL 15+ | Reliable, supports JSON fields for flexible settings storage. |
| **Cache / Queue** | Redis 7+ | For caching generated prompts, rate limiting, and background job queuing. |
| **Authentication** | JWT (via python-jose) + bcrypt | Stateless, secure password hashing. |
| **External APIs** | Google Gemini API (gemini‑1.5‑flash), Replicate / Stability AI / OpenAI | For multimodal understanding and image generation. |
| **Task Queue** | Celery with Redis broker | For handling asynchronous image generation tasks. |
| **Cloud Storage** | AWS S3 or Google Cloud Storage | For storing uploaded images and generated outputs. |

### 2.2 Frontend

| Component | Choice |
|-----------|--------|
| **Framework** | React 18 (TypeScript) with Vite |
| **UI Library** | Tailwind CSS + shadcn/ui components |
| **State Management** | Zustand (lightweight) |
| **File Upload** | react-dropzone, resumable uploads |
| **Image Display** | react‑image‑gallery, masonry layout |
| **Customization** | Dynamic forms with react‑hook‑form + Zod validation |
| **HTTP Client** | axios with interceptors for JWT handling |
| **Routing** | React Router v6 |
| **Animations** | Framer Motion |

### 2.3 Development & Deployment

| Component | Choice |
|-----------|--------|
| **Containerization** | Docker & Docker Compose |
| **Orchestration** | Kubernetes‑ready (optional) |
| **CI/CD** | GitHub Actions or GitLab CI |
| **Monitoring** | Prometheus + Grafana |
| **Logging** | ELK Stack (Elasticsearch, Logstash, Kibana) or Datadog |
| **Testing** | Pytest (backend), Jest + React Testing Library (frontend) |

---

## 3. System Architecture

##
### 3.2 Data Flow

1. **Upload Phase:**
   - User uploads one or more images (single file or directory)
   - Images are validated (format, size, dimensions)
   - Metadata is extracted and stored in PostgreSQL
   - Image files are stored in cloud storage (S3/GCS)
   - Uploaded image references are returned to the frontend

2. **Prompt Enhancement Phase:**
   - User enters a textual prompt and selects output parameters
   - Backend assembles the request with the user's images
   - Gemini Flash receives: image(s) + user prompt + system instruction
   - Gemini returns an enhanced, generation‑ready prompt
   - Enhanced prompt is stored in the database for traceability

3. **Generation Phase:**
   - Enhanced prompt is sent to the selected image generation API
   - Generation task is queued for asynchronous processing
   - Task status is tracked (pending, processing, completed, failed)
   - Generated images are stored in cloud storage
   - Frontend polls for completion and displays results

### 3.3 Component Details

| Component | Description |
|-----------|-------------|
| **Upload Service** | Handles file validation, metadata extraction, and cloud storage operations. Supports both single and batch uploads. |
| **Gemini Orchestrator** | Manages the interaction with Gemini Flash, including prompt engineering, error handling, and response parsing. |
| **Generation Adapter** | Abstract interface for multiple image generation providers. Implements provider-specific logic and error handling. |
| **Task Queue** | Celery workers process generation tasks asynchronously, ensuring the API remains responsive. |
| **Cache Layer** | Redis caches enhanced prompts and frequently accessed settings to improve performance. |
| **Storage Service** | Unified interface for cloud storage operations (upload, download, delete, generate signed URLs). |

---

## 4. Functional Requirements

### 4.1 User Management

- **Registration / Login:**
  - Email and password authentication.
  - Password reset via email (OTP or reset link).
  - Social login (Google, GitHub) optional.

- **Session Management:**
  - JWT-based authentication with refresh tokens.
  - Session timeout configurable (default: 24 hours).

- **User Profile:**
  - View and update profile information.
  - Manage API keys for external services (bring‑your‑own‑key model).
  - View usage statistics and generation history.

- **Personal Library:**
  - View, download, and delete past generations.
  - Organize images into folders/collections.
  - Search and filter by date, preset, or tags.

### 4.2 Image Upload

- **Single Upload:**
  - Drag‑and‑drop or file picker.
  - Supported formats: JPEG, PNG, WEBP, TIFF, HEIC (converted to PNG for processing).
  - Max file size: 50 MB per image (configurable).
  - Progress indicator with upload speed and ETA.

- **Directory Upload:**
  - Preserve folder structure for batch processing.
  - Support for ZIP/TAR archive uploads.
  - Bulk validation with detailed error reporting.
  - Option to process all images with a single prompt.

- **Validation:**
  - File type validation (mime type checking).
  - Dimension constraints (min/max width/height).
  - Virus/malware scanning (optional).

### 4.3 Prompt Engineering & Gemini Integration

- **User Input:**
  - Free‑form text area with character counter (min: 10, max: 1000).
  - Support for multi‑language prompts.
  - Quick‑suggest chips for common prompt structures.


- **Enhanced Prompt Output:**
- Display the enhanced prompt alongside the original.
- Allow manual editing of the enhanced prompt.
- Save enhanced prompt for future reuse.

- **Error Handling:**
- Fallback to original prompt if Gemini fails.
- Detailed error messages for API failures.
- Rate limiting with exponential backoff.

### 4.4 Image Generation

- **Generation Parameters:**
- Number of images: 1–8 (slider or numeric input).
- Aspect ratio / size: dropdown with presets (1:1, 3:4, 16:9, etc.) + custom dimensions.
- Model selection: dropdown (if multiple generation APIs configured).
- Negative prompt (optional): specify what to avoid.
- CFG scale: slider (7–15) for controlling prompt adherence.

- **Supported Generation Services:**
- **Replicate:** Stable Diffusion XL (SDXL), SDXL Turbo.
- **OpenAI:** DALL‑E 3 (HD quality).
- **Google Vertex AI:** Imagen 2.
- **Stability AI:** Stable Diffusion 3 via API.
- *Extensible for additional providers.*

- **Asynchronous Processing:**
- Immediate task ID returned.
- Frontend polls for status updates.
- WebSocket for real‑time progress (optional).
- Email notification on completion (optional).

### 4.5 Output Display & Gallery

- **Gallery View:**
- Responsive masonry or grid layout.
- Thumbnail previews with lazy loading.
- Show original uploaded images side‑by‑side with generated outputs.

- **Image Card:**
- Download button (original resolution).
- Delete button (with confirmation).
- Regenerate button (re‑use same prompt with current settings).
- Metadata display (resolution, size, creation date, used prompt).
- Toggle to view prompt used for generation.

- **Lightbox View:**
- Full‑size image display with zoom.
- Navigation between images (arrow keys).
- Download and share options.
- Compare mode: view original vs generated side‑by‑side.

- **Filtering & Sorting:**
- Filter by date range, preset, or tags.
- Sort by date (newest/oldest), size, or name.

### 4.6 Workspace Customization

- **Dynamic Parameters:**

| Parameter | Description | Options |
|-----------|-------------|---------|
| **Business Model** | The industry or domain of the project | eCommerce, Real Estate, Fashion, Architecture, Automotive, Food & Beverage, Travel, Education, Healthcare, Entertainment, Technology |
| **Niche** | Specific sub-category within the business model | Product Photography, Interior Design, Landscape, Portrait, Abstract, Concept Art, Architectural Visualization, Food Styling, Fashion Editorial |
| **Output Design Type** | Visual style of the generated image | Photorealistic, Artistic, Vector Illustration, Sketch/Line Art, 3D Render, Pixel Art, Watercolor, Oil Painting |
| **Style** | Aesthetic mood or era | Minimalist, Vintage, Futuristic, Cyberpunk, Steampunk, Boho, Scandinavian, Industrial, Elegant, Bold & Vibrant |
| **Size / Aspect Ratio** | Output dimensions | Square (1:1), Portrait (3:4), Landscape (16:9), Cinema (21:9), Square (4:4), Custom (user-defined) |

- **Preloaded Suggestions:**
- Each parameter has a dropdown with curated options.
- Each option includes a short description and an icon.
- Options are filterable and searchable.
- Contextual tooltips explain the impact of each choice.

- **Preset Management:**
- Save current settings as a named preset.
- Load system defaults or user‑saved presets.
- Share presets via URL (optional).
- Organize presets into categories.

- **Workspace Adaptation:**
- CSS variables change based on selected Business Model:
  - *eCommerce* → Clean white, blue accents.
  - *Architecture* → Dark theme, monochrome.
  - *Fashion* → Minimalist, pastel/beige tones.
  - *Real Estate* → Earth tones, professional.
- Layout adjusts based on the selected Niche (e.g., Landscape prioritizes wide image display).

---

## 5. API Endpoints

**Base URL:** `/api/v1`  
**Authentication:** Bearer JWT token (except for public endpoints)

### 5.1 Authentication

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| POST | `/auth/register` | Register new user | `{ email, password, full_name }` | `{ user_id, email }` |
| POST | `/auth/login` | Login, returns JWT | `{ email, password }` | `{ access_token, refresh_token, user }` |
| POST | `/auth/refresh` | Refresh access token | `{ refresh_token }` | `{ access_token }` |
| POST | `/auth/logout` | Logout (blacklist token) | - | `{ message }` |
| GET | `/auth/me` | Get current user info | - | `{ user }` |
| POST | `/auth/forgot-password` | Request password reset | `{ email }` | `{ message }` |
| POST | `/auth/reset-password` | Reset password with token | `{ token, new_password }` | `{ message }` |

### 5.2 Upload

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| POST | `/upload/single` | Upload a single image | `multipart/form-data` with `file` | `{ file_id, metadata }` |
| POST | `/upload/directory` | Upload a directory (ZIP) | `multipart/form-data` with `file` | `{ file_ids: [], count }` |
| POST | `/upload/batch` | Upload multiple files | `multipart/form-data` with `files[]` | `{ file_ids: [], count }` |
| GET | `/upload/{file_id}` | Get file metadata and signed URL | - | `{ metadata, download_url }` |
| DELETE | `/upload/{file_id}` | Delete uploaded file | - | `{ message }` |
| GET | `/upload/list` | List all user uploads | Query: `page`, `limit`, `sort` | `{ items: [], total, page, limit }` |

### 5.3 Generation

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| POST | `/generate` | Submit a generation task | `{ prompt, image_ids: [], generation_params, preset_id? }` | `{ task_id, status }` |
| GET | `/generate/{task_id}` | Get task status | - | `{ task_id, status, progress, error? }` |
| GET | `/generate/{task_id}/result` | Get generated image metadata | - | `{ task_id, enhanced_prompt, images: [] }` |
| POST | `/generate/regenerate/{task_id}` | Regenerate with same parameters | `{ generation_params_override? }` | `{ new_task_id }` |
| POST | `/generate/cancel/{task_id}` | Cancel a pending task | - | `{ message }` |

**Generation Parameters Schema:**
```json
{
"model": "stable-diffusion-xl",
"num_images": 2,
"aspect_ratio": "16:9",
"width": 1024,
"height": 576,
"negative_prompt": "blurry, distorted",
"cfg_scale": 7.5,
"style": "minimalist"
}
┌─────────────┐       ┌──────────────┐       ┌──────────────────┐
│   users     │       │   uploads    │       │ generation_tasks │
│─────────────│       │──────────────│       │──────────────────│
│ id (PK)     │◄──────│ user_id (FK) │       │ id (PK)          │
│ email       │       │ id (PK)      │       │ user_id (FK)     │
│ password    │       │ original_name│       │ original_prompt  │
│ full_name   │       │ stored_path  │       │ enhanced_prompt  │
│ created_at  │       │ mime_type    │       │ generation_params│
│ updated_at  │       │ width        │       │ preset_id (FK)   │
└─────────────┘       │ height       │──────►│ status           │
                      │ size_bytes   │       │ created_at       │
                      │ uploaded_at  │       │ completed_at     │
                      │ is_deleted   │       └──────────────────┘
                      └──────────────┘                │
                                                      │
┌─────────────┐       ┌──────────────┐                │
│   presets   │       │   settings   │       ┌────────▼─────────┐
│─────────────│       │──────────────│       │ generated_images │
│ id (PK)     │       │ user_id (PK)│       │──────────────────│
│ user_id (FK)│       │ default_model│       │ id (PK)          │
│ name        │       │ default_num  │       │ task_id (FK)     │
│ business_   │       │ api_keys     │       │ stored_path      │
│  model      │       └──────────────┘       │ width            │
│ niche       │                              │ height           │
│ design_type │                              │ size_bytes       │
│ style       │                              │ created_at       │
│ aspect_ratio│                              └──────────────────┘
│ gen_params  │
│ is_default  │
│ created_at  │
└─────────────┘
7. Frontend Design
7.1 Design Principles
Aesthetic & Modern: Clean typography, generous whitespace, subtle animations, and a polished feel.

Responsive: Optimized for desktop (primary), tablet, and mobile with adaptive layouts.

Customizable Workspace: Left sidebar for uploaded images, central canvas/prompt area, right panel for settings & presets.

Dark / Light Mode: Toggle available with system preference detection.

7.2 Visual Language
Element	Specification
Primary Color	#6C63FF (Purple)
Secondary Color	#00D4FF (Cyan)
Neutral Background	#F8F9FA (Light) / #1A1A2E (Dark)
Typography	Inter (sans-serif) for UI, Playfair Display for headings
Spacing System	4px, 8px, 16px, 24px, 32px, 48px, 64px, 96px
Border Radius	8px (standard), 12px (cards), 50% (avatars)
Transitions	200ms ease-in-out
7.3 Page Layout
text
┌──────────────────────────────────────────────────────────────────────────────┐
│  App Bar: Logo | Workspace Name | Search | Notifications | User Avatar    │
├──────────────┬───────────────────────────────────────┬──────────────────────┤
│  Sidebar     │  Main Workspace                       │  Right Panel         │
│  (260px)     │  ┌─────────────────────────────────┐  │  (320px)            │
│              │  │  Prompt Input & Generation       │  │  ┌────────────────┐ │
│  ┌────────┐  │  │  Controls                       │  │  │ Presets        │ │
│  │Upload   │  │  └─────────────────────────────────┘  │  │ (System & User)│ │
│  │History  │  │  ┌─────────────────────────────────┐  │  ├────────────────┤ │
│  │(Collaps)│  │  │  Image Gallery                  │  │  │ Parameters     │ │
│  └────────┘  │  │  (Uploaded & Generated)          │  │  │ Business Model │ │
│              │  │                                   │  │  │ Niche          │ │
│  ┌────────┐  │  │  ┌───┐ ┌───┐ ┌───┐ ┌───┐       │  │  │ Design Type    │ │
│  │Folders │  │  │  │   │ │   │ │   │ │   │       │  │  │ Style          │ │
│  │(Tree)  │  │  │  └───┘ └───┘ └───┘ └───┘       │  │  │ Aspect Ratio   │ │
│  └────────┘  │  │                                   │  │  └────────────────┘ │
│              │  │                                   │  │  ┌────────────────┐ │
│  ┌────────┐  │  │                                   │  │  │ Save Preset    │ │
│  │Tags    │  │  │                                   │  │  │ Generate Btn   │ │
│  └────────┘  │  │                                   │  │  └────────────────┘ │
├──────────────┴───────────────────────────────────────┴──────────────────────┤
│  Status Bar: Task Progress | Generation Time | Storage Usage               │
└──────────────────────────────────────────────────────────────────────────────┘
7.4 Key UI Components
a) Upload Area
Drop Zone: Large area with dashed border, drag‑and‑drop support.

Buttons: "Browse Files" and "Upload Directory" (with webkitdirectory attribute).

Progress: Multiple file progress bars with percentages and cancel buttons.

Preview: Thumbnail previews of uploaded images before confirmation.

b) Prompt Input
Text Area: Large, with auto‑resize, character counter (10–1000).

Quick Chips: Pre‑populated prompt templates (e.g., "Create a product shot of...").

Image Attachments: Show thumbnails of attached images with remove option.

Enhance Button: Triggers Gemini processing with loading animation.

Enhanced Prompt: Display below input, editable, with copy functionality.

c) Generation Controls
Model Selector: Dropdown with model names and badges (Fast, HD, etc.).

Number of Images: Slider with numeric label (1–8).

Aspect Ratio: Dropdown with common presets and custom dimension inputs.

Negative Prompt: Collapsible section for optional input.

Advanced Parameters: CFG scale, steps (for diffusion models) – collapsible.

d) Preset Panel
Tabs: "System Defaults" and "My Presets".

Preset Cards: Each shows name and parameter tags (e.g., "eCommerce | Photorealistic").

Actions: Apply, Edit, Delete (with confirmation), Duplicate.

Save Preset: Modal with form to name and save current settings.

e) Gallery
Layout Toggle: Grid (masonry) vs List view.

Image Cards: Thumbnail, creation date, prompt snippet on hover.

Actions on Card: Download, Regenerate, Delete, Details.

Lightbox: Full‑screen overlay with navigation, zoom, and metadata panel.

Bulk Selection: Checkboxes for batch operations.

f) Workspace Customization Panel
Dynamic Dropdowns: Business Model, Niche, Design Type, Style.

Contextual Help: Info icon next to each dropdown with tooltip.

Live Preview: Show a mockup of how the workspace would look with selected settings.

Reset Button: Reset all parameters to default.

7.5 Preloaded Suggestions
The frontend fetches from /settings/options to populate dropdowns:

Business Models
🏢 eCommerce – Product photography, catalog images.

🏠 Real Estate – Property interiors, exteriors, virtual staging.

👗 Fashion – Apparel, accessories, editorial looks.

🏛️ Architecture – Building designs, blueprints, concept renderings.

🚗 Automotive – Vehicle shots, concept cars, racing scenes.

🍽️ Food & Beverage – Plated dishes, ingredients, restaurant scenes.

✈️ Travel – Landscapes, cityscapes, cultural experiences.

🎓 Education – Illustrations, diagrams, learning materials.

🏥 Healthcare – Medical illustrations, wellness visuals.

🎮 Entertainment – Game art, movie posters, character designs.

Niches
📷 Product Photography – Clean, detailed product shots.

🛋️ Interior Design – Room layouts, furniture staging.

🌄 Landscape – Nature, cityscapes, outdoor scenes.

👤 Portrait – Human subjects, expressions, fashion.

🎨 Abstract – Non‑representational art.

🧙 Concept Art – Fantasy, sci‑fi, world‑building.

🏗️ Architectural Visualization – 3D building renders.

🍜 Food Styling – Plating, ingredient close‑ups.

Design Types
📸 Photorealistic – Highly detailed, true‑to‑life.

🎨 Artistic – Painterly, impressionistic.

📐 Vector Illustration – Clean lines, flat colors.

✏️ Sketch/Line Art – Pencil or ink style.

🏗️ 3D Render – Digital 3D modeling style.

🟦 Pixel Art – Retro, blocky style.

🖌️ Watercolor – Soft, blended colors.

🎭 Oil Painting – Thick brush strokes, rich texture.

Styles
⬜ Minimalist – Clean, simple, lots of white space.

🕰️ Vintage – Retro, worn, sepia tones.

🚀 Futuristic – Neon, metallic, high‑tech.

🤖 Cyberpunk – Dark, neon, dystopian.

⚙️ Steampunk – Brass, gears, Victorian.

🌸 Boho – Earthy, eclectic, patterned.

❄️ Scandinavian – Light, minimal, natural materials.

🏭 Industrial – Raw, exposed, urban.

Aspect Ratios
⬜ Square (1:1) – Balanced, social media friendly.

📱 Portrait (3:4) – Ideal for mobile and print.

🖥️ Landscape (16:9) – Standard widescreen.

🎬 Cinema (21:9) – Ultra‑wide cinematic.

📐 Custom – User‑defined width and height.

8. Integration with Gemini Flash
8.1 Gemini API Usage
Setting	Value
Model	gemini-1.5-flash (fast) or gemini-1.5-pro (higher quality)
Input Format	Images as mime_type + data (base64) or uri (cloud URL)
Max Images per Request	10
Max Tokens	8192 (output)
Temperature	0.7 (balanced creativity)

8.2 Request Structure
python
# Example Gemini API call (Python)
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

# Prepare content parts
content_parts = [
    image_part,  # Uploaded image(s)
    f"User request: {user_prompt}",
    f"Business Model: {business_model}",
    f"Niche: {niche}",
    f"Design Type: {design_type}",
    f"Style: {style}"
]

# System instruction
system_instruction = """
You are an expert prompt engineer for image generation. Your task is to analyze the provided images and the user's request, then craft a detailed, vivid prompt optimized for text-to-image models. Return ONLY the enhanced prompt as plain text.
"""

response = model.generate_content(
    contents=content_parts,
    system_instruction=system_instruction
)

enhanced_prompt = response.text
8.3 Prompt Engineering Best Practices
System Instruction Template:

text
You are a creative prompt engineer specializing in {business_model} with a focus on {niche}. The output should be {design_type} style with a {style} aesthetic.

Given the attached images and the user's request:
1. Analyze the images: subject, composition, colors, lighting, mood.
2. Understand the user's intent and desired outcome.
3. Synthesize a single, cohesive prompt that:
   - Describes the scene in vivid detail.
   - Incorporates the {style} aesthetic.
   - Matches the {design_type} quality.
   - Considers the {business_model} context.

The final prompt should be 50-200 words, written in a single paragraph, with no additional commentary.
Example Enhanced Prompt Output:

text
"Create a photorealistic product photography image of a modern minimalist watch on a polished marble surface. The watch has a sleek silver metal band with a white ceramic dial, and is positioned at a 30-degree angle with the strap elegantly draped. Soft natural window lighting from the left creates gentle shadows that accentuate the texture of the marble, while a subtle warm backlight illuminates the watch face. The composition should feel premium and sophisticated, suitable for an eCommerce product catalog."
8.4 Error Handling & Retry Logic
Scenario	Action
Timeout (>30s)	Retry with exponential backoff (1s, 2s, 4s, 8s)
Rate Limit (429)	Wait and retry after 60s
Invalid API Key	Return user-friendly error, suggest checking API key
Invalid Image Format	Convert to supported format or return error
Empty Response	Fallback to original prompt with warning
9. Image Generation Service Integration
9.1 Adapter Pattern Architecture
python
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class ImageGenerationAdapter(ABC):
    """Base adapter for image generation services"""
    
    @abstractmethod
    async def generate(self, prompt: str, params: Dict[str, Any]) -> List[ImageResult]:
        """Generate images from a prompt and parameters"""
        pass
    
    @abstractmethod
    async def get_status(self, task_id: str) -> GenerationStatus:
        """Get the status of an ongoing generation task"""
        pass

class ReplicateAdapter(ImageGenerationAdapter):
    def __init__(self, api_key: str):
        self.client = replicate.Client(api_key=api_key)
    
    async def generate(self, prompt: str, params: Dict) -> List[ImageResult]:
        # Implementation specific to Replicate API
        pass

class OpenAIAdapter(ImageGenerationAdapter):
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
    
    async def generate(self, prompt: str, params: Dict) -> List[ImageResult]:
        # Implementation specific to DALL-E API
        pass
9.2 Supported Providers
Provider	Model(s)	Best For	Cost (est.)
Replicate	SDXL, SDXL Turbo, SD3	High quality, fast, community models	$0.002–0.005 per image
OpenAI	DALL-E 3	Exceptional quality, prompt understanding	$0.04–0.08 per image
Google Vertex AI	Imagen 2	Integration with Gemini ecosystem	~$0.03 per image
Stability AI	Stable Diffusion 3	Cutting-edge quality, customization	$0.005 per image
9.3 Generation Parameters Mapping
Parameter	Replicate	OpenAI	Vertex AI
Prompt	prompt	prompt	prompt
Negative Prompt	negative_prompt	N/A	negative_prompt
Num Images	num_outputs	n	num_images
Aspect Ratio	Calculated via size	size (enum)	N/A (fixed)
Size	width/height	N/A	N/A
CFG Scale	guidance_scale	N/A	N/A
Steps	num_inference_steps	N/A	N/A
Seed	seed	seed	seed
9.4 Asynchronous Processing Flow
text
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Frontend   │    │  FastAPI     │    │  Redis       │
│   (User)     │    │  (Backend)   │    │  (Queue)     │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                   │
       │ POST /generate    │                   │
       │──────────────────>│                   │
       │                   │                   │
       │                   │ Enqueue task      │
       │                   │──────────────────>│
       │                   │                   │
       │ { task_id }       │                   │
       │<──────────────────│                   │
       │                   │                   │
       │ GET /status       │                   │
       │──────────────────>│                   │
       │                   │                   │
       │                   │ Get status        │
       │                   │<──────────────────│
       │                   │                   │
       │ { status }        │                   │
       │<──────────────────│                   │
       │                   │                   │
       │ Polling repeats   │                   │
       │ until complete    │                   │
       │                   │                   │
       │                   │  ┌─────────────────┐
       │                   │  │  Celery Worker  │
       │                   │  │─────────────────│
       │                   │  │ Pop task from   │
       │                   │  │ Redis queue     │
       │                   │  │                 │
       │                   │  │ Call Gemini     │
       │                   │  │ Call Generator │
       │                   │  │ Save results    │
       │                   │  └─────────────────┘
       │                   │                   │
       │ GET /result       │                   │
       │──────────────────>│                   │
       │                   │                   │
       │ { images }        │                   │
       │<──────────────────│                   │
10. Implementation Plan (Phase‑wise)
Phase 1: Foundation (Weeks 1‑2)
Backend:

Set up project repository and development environment

Configure Docker Compose for local development (FastAPI, PostgreSQL, Redis)

Implement user authentication (JWT + bcrypt)

Design and implement database schema (migrations with Alembic)

Create base FastAPI app with health check endpoints

Frontend:

Initialize React + TypeScript project with Vite

Set up Tailwind CSS + shadcn/ui

Implement routing (React Router)

Create authentication pages (Login, Register)

Configure Axios with JWT interceptor

Deliverable: Working authentication system with basic API and frontend skeleton.

Phase 2: Upload & Storage (Weeks 3‑4)
Backend:

Implement cloud storage abstraction (S3/GCS)

Create upload endpoints (single and batch)

Add image validation (format, size, dimensions)

Extract and store image metadata

Implement directory upload support (ZIP processing)

Frontend:

Build drag‑and‑drop upload component

Implement progress indicators for uploads

Create file list and thumbnail previews

Add directory upload support with structure preservation

Deliverable: Fully functional upload system with cloud storage integration.

Phase 3: Gemini Integration (Weeks 5‑6)
Backend:

Set up Google Gemini API client

Design system instruction templates

Implement prompt enhancement endpoint

Add error handling and retry logic

Cache enhanced prompts in Redis

Frontend:

Build prompt input interface

Implement "Enhance with Gemini" button

Display enhanced prompt with diff view

Add editing capability for enhanced prompt

Deliverable: Working Gemini integration with prompt enhancement.

Phase 4: Image Generation (Weeks 7‑8)
Backend:

Implement adapter pattern for generation services

Add Replicate SDK integration (initial provider)

Set up Celery + Redis for background tasks

Create generation endpoints (submit, status, result)

Implement webhook support for async generation

Frontend:

Build generation parameter controls

Add model selection dropdown

Implement task polling and status display

Create gallery view for generated images

Deliverable: End‑to‑end generation pipeline (Gemini → Image Gen → Display).

Phase 5: Workspace & Presets (Weeks 9‑10)
Backend:

Add presets CRUD API

Implement default presets (system)

Add /settings/options endpoint

Store user preferences

Frontend:

Build workspace layout with three panels

Implement presets management UI

Create dynamic parameter dropdowns

Add workspace theme adaptation based on business model

Implement dark/light mode toggle

Deliverable: Fully customizable workspace with presets.

Phase 6: Polishing & Testing (Weeks 11‑12)
Backend:

Write comprehensive unit and integration tests (Pytest)

Implement API rate limiting

Add request/response validation

Improve error handling and logging

Performance optimization (query optimization, caching)

Frontend:

Implement responsive design for mobile/tablet

Add loading states and skeleton screens

Perform accessibility audit (WCAG 2.1)

Optimize image loading (lazy loading, WebP conversion)

Write component tests (Jest + React Testing Library)

All:

Create deployment configuration (Docker, Kubernetes)

Set up CI/CD pipeline (GitHub Actions)

Write user documentation

Conduct beta user testing and iterate

Deliverable: Production‑ready application with comprehensive testing.

11. Non‑Functional Requirements
11.1 Performance
Metric	Target
API Response Time	< 200ms (p95) for non‑generation endpoints
Gemini Enhancement	< 5 seconds (p90)
Image Generation	< 60 seconds (p95) for SDXL
Page Load Time	< 2 seconds (first contentful paint)
Concurrent Users	Support 100+ concurrent sessions
11.2 Security
Authentication: JWT with short‑lived access tokens (15 min) and refresh tokens (7 days).

Encryption: TLS 1.3 for all traffic; API keys stored encrypted (AES‑256).

Input Validation: All user inputs validated and sanitized.

Rate Limiting: Prevent abuse (100 requests per minute per user).

File Security: Uploaded files scanned (ClamAV optional); stored with random UUID names.

CORS: Restrict to whitelisted origins.

11.3 Scalability
Stateless Backend: Easy horizontal scaling.

Database: Connection pooling, read replicas for heavy queries.

Cache: Redis for session storage and frequent queries.

Storage: Cloud storage with CDN for image delivery.

Queue: Celery workers auto‑scaled based on queue depth.

11.4 Availability & Reliability
Target Uptime: 99.9% (monthly).

Backup: Daily database backups, point‑in‑time recovery.

Monitoring: Health checks, performance metrics, error alerts.

Disaster Recovery: Multi‑region cloud storage replication.

11.5 Extensibility
Modular Architecture: Easy to add new generation providers.

Plugin System: For custom prompt engineering templates.

Webhooks: For integration with external applications.

API Versioning: All endpoints versioned for backward compatibility.

11.6 Accessibility (WCAG 2.1 AA)
Keyboard navigation support.

Screen reader compatible ARIA labels.

Sufficient color contrast (4.5:1 minimum).

Focus indicators for all interactive elements.

Alternative text for all images.

12. Conclusion
nanoImage combines the reasoning power of Gemini Flash with state‑of‑the‑art image generation, delivering a versatile, user‑friendly web application. Its workspace adapts to the user’s domain, providing tailored suggestions and an aesthetic interface. The modular architecture ensures future enhancements can be integrated with minimal friction.

This specification serves as the blueprint for development, covering all essential aspects from backend stack to frontend design, and is ready for implementation.

13. Appendix
13.1 Environment Variables (.env)
bash
# Backend
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/nanoimage
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Gemini
GEMINI_API_KEY=your-gemini-api-key

# Cloud Storage
S3_BUCKET_NAME=nanoimage-storage
S3_REGION=us-east-1
S3_ACCESS_KEY=your-access-key
S3_SECRET_KEY=your-secret-key
S3_ENDPOINT_URL=https://s3.amazonaws.com  # Optional for custom endpoints

# Image Generation
REPLICATE_API_TOKEN=your-replicate-token
OPENAI_API_KEY=your-openai-key
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
13.2 Docker Compose Template
yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: nanoimage
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: nanoimage
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  backend:
    build: ./backend
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    environment:
      - DATABASE_URL=postgresql+asyncpg://nanoimage:secret@db:5432/nanoimage
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis

  celery_worker:
    build: ./backend
    command: celery -A app.worker worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql+asyncpg://nanoimage:secret@db:5432/nanoimage
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/0
    volumes:
      - ./backend:/app
    depends_on:
      - db
      - redis

  frontend:
    build: ./frontend
    command: npm run dev
    volumes:
      - ./frontend:/app
      - /app/node_modules
    ports:
      - "5173:5173"
    depends_on:
      - backend

volumes:
  postgres_data:
  redis_data:
13.3 Sample Project Structure
text
nanoImage/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── upload.py
│   │   │   ├── generation.py
│   │   │   ├── presets.py
│   │   │   └── gallery.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── database.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── upload.py
│   │   │   ├── generation.py
│   │   │   └── preset.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── gemini.py
│   │   │   ├── generation/
│   │   │   │   ├── base.py
│   │   │   │   ├── replicate.py
│   │   │   │   ├── openai.py
│   │   │   │   └── vertex.py
│   │   │   ├── storage.py
│   │   │   └── task_queue.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── generation.py
│   │   │   └── presets.py
│   │   └── main.py
│   ├── tests/
│   ├── migrations/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── auth/
│   │   │   ├── upload/
│   │   │   ├── generation/
│   │   │   ├── gallery/
│   │   │   ├── presets/
│   │   │   └── layout/
│   │   ├── pages/
│   │   │   ├── Login.tsx
│   │   │   ├── Register.tsx
│   │   │   ├── Workspace.tsx
│   │   │   └── Gallery.tsx
│   │   ├── hooks/
│   │   ├── stores/
│   │   ├── services/
│   │   ├── utils/
│   │   ├── types/
│   │   └── styles/
│   ├── public/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   └── Dockerfile
│
├── docker-compose.yml
├── README.md
└── .gitignore
13.4 UI Design Mockups (ASCII Reference)
Workspace View
text
┌──────────────────────────────────────────────────────────────────────────┐
│  ☰ nanoImage   ─── Dashboard   Gallery   Presets   🔔  👤 John         │
├──────────────┬──────────────────────────────────────┬───────────────────┤
│  📂 Upload   │  ✏️ Prompt Input                     │  ⚙️ Settings      │
│  ──────────  │  ┌────────────────────────────────┐ │  ──────────────  │
│  📁 Images   │  │ "Create a cozy living room..." │ │  Business Model  │
│  📁 Projects │  │                                │ │  [eCommerce ▼]   │
│  📁 Folder   │  └────────────────────────────────┘ │                   │
│              │  [🔮 Enhance with Gemini]            │  Niche            │
│  📅 Recent   │  Enhanced Prompt:                    │  [Product ▼]     │
│  ──────────  │  ┌────────────────────────────────┐ │                   │
│  img1.jpg    │  │ "Photorealistic living room..." │ │  Design Type     │
│  img2.png    │  └────────────────────────────────┘ │  [Photo ▼]       │
│  img3.webp   │                                      │                   │
│              │  🎨 Generation Controls              │  Style            │
│  🏷️ Tags    │  ┌────────────────────────────────┐ │  [Minimalist ▼]  │
│  ──────────  │  │ Model: [SDXL ▼]  Num: [2]     │ │                   │
│  #product    │  │ Aspect: [16:9 ▼]  Size: 1024x576│ │  Aspect Ratio    │
│  #interior   │  │ Neg prompt: [blurry, distorted]│ │  [16:9 ▼]        │
│              │  └────────────────────────────────┘ │                   │
│              │  [💾 Save Preset]  [🚀 Generate]    │  ──────────────  │
│              │                                      │  [Save Preset]   │
│              │  🖼️ Gallery (Uploaded | Generated)   │  [Reset]         │
│              │  ┌────┐ ┌────┐ ┌────┐ ┌────┐       │                   │
│              │  │    │ │    │ │    │ │    │       │                   │
│              │  └────┘ └────┘ └────┘ └────┘       │                   │
├──────────────┴──────────────────────────────────────┴───────────────────┤
│  ⏳ Task: Generating... 45%  |  Storage: 2.3GB / 10GB  |  v1.0.0      │
└──────────────────────────────────────────────────────────────────────────┘
End of Specification

How to Use This Document
Save as markdown: Copy the entire content and save as nano-image-spec.md

Import to project management: Use as a reference for sprint planning

Share with team: Distribute to backend, frontend, and QA engineers

Update as needed: Revise sections as requirements evolve

Document Version: 1.0.0
Last Updated: June 2026
Author: nanoImage Development Team

text

---

## How to Download

Since I can't create a direct download link, here are two ways to get this file:

### Method 1: Copy and Save (Recommended)
1. Select all the text above (everything between the ```markdown fences)
2. Copy to your clipboard (Ctrl+C / Cmd+C)
3. Open a text editor (VS Code, Notepad++, Sublime Text, etc.)
4. Paste the content (Ctrl+V / Cmd+V)
5. Save as `nano-image-spec.md`

### Method 2: Browser Console (Quick One-Liner)
Open your browser's developer console (F12) and paste this:

```javascript
// Copy to clipboard
copy(`[PASTE THE ENTIRE MARKDOWN CONTENT HERE]`)
Method 3: Use a Code Block
If you're viewing this in a markdown previewer, you can often right-click and select "Save As" or "Download" from the context menu.

Quick Setup Commands
Once you have the file, you can start using it:

bash
# Create project structure
mkdir nanoImage && cd nanoImage
touch nano-image-spec.md
# Then paste the content into the file

# Optional: Convert to PDF (if you have pandoc)
pandoc nano-image-spec.md -o nano-image-spec.pdf --pdf-engine=xelatex

# Or open in your favorite markdown viewer
# VS Code: Ctrl+Shift+V to preview
# Typora, Obsidian, etc.
The specification is now ready for your development team to reference!



