from app.schemas.generation import GenerationTaskCreate


IMAGE_TYPE_LABELS = {
    "main_image": "ecommerce product main image",
    "lifestyle_scene": "ecommerce lifestyle scene image",
    "detail_image": "ecommerce detail page image",
    "detail_set": "ecommerce detail page image set",
    "campaign": "ecommerce campaign creative",
    "social_post": "social media product post",
    "variant_batch": "ecommerce image variant",
}

TEMU_COMPLIANCE_PROMPT = [
    "Apply Temu product image compliance as an additional platform standard.",
    "Use a clean ecommerce composition suitable for platform upload; prefer 1:1 square product images and 1600x1600 export when the selected output size allows it.",
    "Keep the product complete with intact edges, stable center of gravity, realistic perspective, and proportional scale.",
    "For main images, use a single product hero with the longest side filling the frame while keeping safe margins on all sides.",
    "For scene images, keep the background clean, uncluttered, realistic, and limited to no more than three dominant colors.",
    "For combination products, keep every item physically plausible in scale, perspective, placement, and scene logic.",
    "For model scenes, keep the model natural and realistic, with normal facial and body proportions, no heavy filters, and the product clearly visible.",
    "Do not create collages, split-screen layouts, text overlays, Chinese text, watermark, sticker labels, price tags, ratings, promotional claims, or messy props.",
    "Output should feel like clean commercial ecommerce photography, PNG/JPG ready, platform-safe and upload-friendly.",
]


def optimize_user_prompt(value: str | None) -> str | None:
    if not value:
        return None

    normalized = " ".join(value.replace("\n", " ").split())
    if not normalized:
        return None

    return (
        "Refined creative direction: "
        f"{normalized}. "
        "Translate this into a commercially usable ecommerce visual with a clear product hero, "
        "controlled composition, realistic lighting, platform-safe negative space, and no unsupported product claims."
    )


def build_prompt(request: GenerationTaskCreate) -> str:
    params = request.params
    normalized_prompt = " ".join(params.prompt.replace("\n", " ").split()) if params.prompt else None
    optimized_prompt = optimize_user_prompt(params.prompt) if params.optimize_prompt else normalized_prompt
    prompt_parts = [
        f"Create a high-quality {IMAGE_TYPE_LABELS[request.image_type]}.",
        f"Project id: {request.project_id}.",
    ]
    if request.product_id:
        prompt_parts.append(f"Product id: {request.product_id}.")
    if request.source_asset_ids:
        prompt_parts.append(
            "Use the uploaded source image as the factual product reference and preserve its visible appearance."
        )
    if params.platform and params.platform.lower() == "temu":
        prompt_parts.extend(TEMU_COMPLIANCE_PROMPT)
    if optimized_prompt:
        if params.optimize_prompt:
            prompt_parts.append(optimized_prompt)
        else:
            prompt_parts.append(f"User creative direction: {optimized_prompt}.")
    if params.scene:
        prompt_parts.append(f"Scene: {params.scene}.")
    if params.background:
        prompt_parts.append(f"Background: {params.background}.")
    if params.style:
        prompt_parts.append(f"Style: {params.style}.")
    if params.lighting:
        prompt_parts.append(f"Lighting: {params.lighting}.")
    if params.composition:
        prompt_parts.append(f"Composition: {params.composition}.")
    prompt_parts.extend(
        [
            "Keep the product as the clear hero.",
            "Preserve the product's core shape, color, structure, quantity, and visible details.",
            "Do not add logos, certifications, prices, ratings, or claims unless explicitly provided.",
            "Avoid misleading effects or exaggerated product performance.",
            "Do not use protected brands, characters, celebrities, competitor logos, or unsupported IP elements.",
            "Exact text should be added by the frontend as an editable overlay when possible.",
        ]
    )
    if request.negative_constraints:
        prompt_parts.append("Additional constraints: " + "; ".join(request.negative_constraints))
    return "\n".join(prompt_parts)
