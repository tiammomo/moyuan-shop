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


def build_prompt(request: GenerationTaskCreate) -> str:
    params = request.params
    prompt_parts = [
        f"Create a high-quality {IMAGE_TYPE_LABELS[request.image_type]}.",
        f"Project id: {request.project_id}.",
    ]
    if request.product_id:
        prompt_parts.append(f"Product id: {request.product_id}.")
    if params.prompt:
        prompt_parts.append(f"User direction: {params.prompt}")
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
        ]
    )
    if request.negative_constraints:
        prompt_parts.append("Additional constraints: " + "; ".join(request.negative_constraints))
    return "\n".join(prompt_parts)
