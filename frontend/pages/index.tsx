import Head from 'next/head';
import Chat from '../components/Chat';

export default function Home() {
  return (
    <>
      <Head>
        <title>Multi-Agent Chat</title>
      </Head>
      <Chat />
    </>
  );
}
