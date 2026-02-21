import { useState, useEffect } from "react";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

interface Election {
  id: string;
  name: string;
  year: number;
  type: string;
  statistics: {
    total_candidates: number;
    total_constituencies: number;
    total_parties: number;
    total_winners: number;
    top_parties?: Array<{
      name: string;
      short_name: string;
      seats_won: number;
    }>;
  };
}

export function useElection(electionId: string | null) {
  const [election, setElection] = useState<Election | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!electionId) {
      setLoading(false);
      return;
    }

    const fetchElection = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${API_BASE_URL}/elections/${electionId}`);
        const data = await response.json();
        if (data.success) {
          setElection(data.data);
          setError(null);
        } else {
          setError(data.error || "Failed to load election");
        }
      } catch (err) {
        setError("Error connecting to API");
        console.error("Error fetching election:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchElection();
  }, [electionId]);

  return { election, loading, error };
}

export function useElections() {
  const [elections, setElections] = useState<Election[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchElections = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${API_BASE_URL}/elections`);
        const data = await response.json();
        if (data.success) {
          setElections(data.data);
          setError(null);
        } else {
          setError(data.error || "Failed to load elections");
        }
      } catch (err) {
        setError("Error connecting to API");
        console.error("Error fetching elections:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchElections();
  }, []);

  return { elections, loading, error };
}
