import { useEffect, useState, type MouseEvent } from "react";
import { createCheckout, fetchTiers, type Tier } from "./api/client";
import Hero from "./components/Hero";
import Pricing from "./components/Pricing";
import Checkout from "./components/Checkout";
import PaymentSuccess from "./pages/PaymentSuccess";

function MainApp() {
  const [tiers, setTiers] = useState<Tier[]>([]);
  const [selectedTier, setSelectedTier] = useState<string | null>(null);
  const [email, setEmail] = useState("");
  const [payLoading, setPayLoading] = useState(false);
  const [payError, setPayError] = useState<string | null>(null);

  useEffect(() => {
    fetchTiers().then(setTiers).catch(console.error);
  }, []);

  const selected = tiers.find((t) => t.id === selectedTier) ?? null;

  const scrollTo = (id: string) => {
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });
  };

  const handlePay = async () => {
    if (!selectedTier || !email.trim()) return;
    setPayLoading(true);
    setPayError(null);
    try {
      const checkout = await createCheckout(selectedTier, email.trim());
      window.location.href = checkout.confirmation_url;
    } catch (e) {
      setPayError(e instanceof Error ? e.message : "Payment error");
      setPayLoading(false);
    }
  };

  return (
    <>
      <Hero onCta={() => scrollTo("pricing")} />
      <Pricing tiers={tiers} selectedTier={selectedTier} onSelect={setSelectedTier} />
      <Checkout
        tier={selected}
        email={email}
        onEmailChange={setEmail}
        loading={payLoading}
        onPay={handlePay}
      />
      {payError && <p className="error-banner">{payError}</p>}
    </>
  );
}

const NAV_CONFIRM_MSG =
  "\u041f\u0430\u0440\u043e\u043b\u044c \u0435\u0449\u0451 \u0433\u0435\u043d\u0435\u0440\u0438\u0440\u0443\u0435\u0442\u0441\u044f. \u0423\u0439\u0442\u0438 \u043d\u0430 \u0433\u043b\u0430\u0432\u043d\u0443\u044e?";

export default function App() {
  const isSuccessPage = window.location.pathname === "/payment/success";
  const [passwordLoading, setPasswordLoading] = useState(isSuccessPage);

  const handleHomeNav = (event: MouseEvent<HTMLAnchorElement>) => {
    if (isSuccessPage && passwordLoading) {
      event.preventDefault();
      if (window.confirm(NAV_CONFIRM_MSG)) {
        window.location.href = "/";
      }
    }
  };

  return (
    <div className="app">
      <header className="header">
        <a href="/" className="header__logo" onClick={handleHomeNav}>
          Svinopass
        </a>
        <nav className="header__nav">
          <a href="/" onClick={handleHomeNav}>
            {"\u0413\u043b\u0430\u0432\u043d\u0430\u044f"}
          </a>
        </nav>
      </header>

      <main>
        {isSuccessPage ? (
          <PaymentSuccess onWaitingChange={setPasswordLoading} />
        ) : (
          <MainApp />
        )}
      </main>

      <footer className="footer">
        <p>svinopass.ru 2026</p>
      </footer>
    </div>
  );
}