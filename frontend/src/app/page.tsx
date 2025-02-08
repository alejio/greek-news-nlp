'use client'

import { useEffect, useState } from 'react';
import {
  Box,
  Container,
  Heading,
  SimpleGrid,
  Text,
  VStack,
  useToast,
} from '@chakra-ui/react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { api, Article, StancePrediction } from '@/utils/api';

interface StanceStats {
  target: string;
  positive: number;
  negative: number;
  neutral: number;
}

export default function Home() {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const toast = useToast();

  useEffect(() => {
    const fetchArticles = async () => {
      try {
        const data = await api.articles.getAll({ limit: 100 });
        setArticles(data);
      } catch (error) {
        toast({
          title: 'Error fetching articles',
          description: 'Please try again later',
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      } finally {
        setLoading(false);
      }
    };

    fetchArticles();
  }, [toast]);

  const calculateStanceStats = (): StanceStats[] => {
    const statsMap = new Map<string, { positive: number; negative: number; neutral: number }>();

    articles.forEach((article) => {
      article.stance_predictions.forEach((prediction) => {
        const current = statsMap.get(prediction.target) || {
          positive: 0,
          negative: 0,
          neutral: 0,
        };

        switch (prediction.stance.toLowerCase()) {
          case 'positive':
            current.positive += 1;
            break;
          case 'negative':
            current.negative += 1;
            break;
          case 'neutral':
            current.neutral += 1;
            break;
        }

        statsMap.set(prediction.target, current);
      });
    });

    return Array.from(statsMap.entries()).map(([target, stats]) => ({
      target,
      ...stats,
    }));
  };

  const stanceStats = calculateStanceStats();

  if (loading) {
    return (
      <Container maxW="container.xl" py={8}>
        <Text>Loading...</Text>
      </Container>
    );
  }

  return (
    <Container maxW="container.xl" py={8}>
      <VStack spacing={8} align="stretch">
        <Heading as="h1" size="xl">
          Greek Sports News Analysis
        </Heading>

        <Box p={6} bg="white" shadow="sm" borderRadius="lg">
          <Heading as="h2" size="lg" mb={4}>
            Stance Analysis by Target
          </Heading>
          <Box height="400px">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stanceStats}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="target" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="positive" fill="#38A169" name="Positive" />
                <Bar dataKey="negative" fill="#E53E3E" name="Negative" />
                <Bar dataKey="neutral" fill="#718096" name="Neutral" />
              </BarChart>
            </ResponsiveContainer>
          </Box>
        </Box>

        <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6}>
          <Box p={6} bg="white" shadow="sm" borderRadius="lg">
            <Heading as="h2" size="lg" mb={4}>
              Recent Articles
            </Heading>
            <VStack align="stretch" spacing={4}>
              {articles.slice(0, 5).map((article) => (
                <Box key={article.id} p={4} borderWidth={1} borderRadius="md">
                  <Text fontWeight="bold">{article.title}</Text>
                  <Text color="gray.600" fontSize="sm">
                    By {article.blogger.name}
                  </Text>
                </Box>
              ))}
            </VStack>
          </Box>

          <Box p={6} bg="white" shadow="sm" borderRadius="lg">
            <Heading as="h2" size="lg" mb={4}>
              Top Targets
            </Heading>
            <VStack align="stretch" spacing={4}>
              {stanceStats
                .sort((a, b) => (b.positive + b.negative + b.neutral) - (a.positive + a.negative + a.neutral))
                .slice(0, 5)
                .map((stat) => (
                  <Box key={stat.target} p={4} borderWidth={1} borderRadius="md">
                    <Text fontWeight="bold">{stat.target}</Text>
                    <Text color="gray.600" fontSize="sm">
                      {stat.positive + stat.negative + stat.neutral} mentions
                    </Text>
                  </Box>
                ))}
            </VStack>
          </Box>
        </SimpleGrid>
      </VStack>
    </Container>
  );
}
