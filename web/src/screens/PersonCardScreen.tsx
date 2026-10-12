// 인물 카드 화면 — U6 에서 채운다. `#/persons`(목록) 와 `#/persons/:id`(카드) 가 이 화면 하나를 쓴다.
export default function PersonCardScreen({ personId }: { personId: number | null }) {
  return (
    <section
      aria-labelledby="screen-title"
      data-screen="persons"
      data-person-id={personId ?? undefined}
    >
      <h1 id="screen-title" className="text-title font-semibold">인물</h1>
    </section>
  )
}
