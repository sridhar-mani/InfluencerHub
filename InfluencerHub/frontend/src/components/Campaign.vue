<template>
  <div class="d-flex p-4">
    <BCard
      title="Card Title"
      img-src="https://picsum.photos/600/300/?image=25"
      img-alt="Image"
      img-top
      tag="article"
      style="max-width: 15rem; max-height: 20rem"
    >
      <BCardText style="max-height: 40%; font-size: 14px">
        Some quick example text to build on the card title and make up the bulk
        of the card's content.
      </BCardText>

      <BButton href="#" variant="primary">Go somewhere</BButton>
    </BCard>
  </div>
</template>

<script>
export default {
  name: "Campaign",
};
</script>

<style></style>
